const express = require('express');
const router = express.Router();
const multer = require('multer');
const xlsx = require('xlsx');
const fs = require('fs');
const path = require('path');
const PackingList = require('../models/PackingList');
const Product = require('../models/Product');
const mongoose = require('mongoose');
const { verifyToken: auth } = require('../middleware/auth');

// 确保上传目录存在
const uploadDir = path.join(__dirname, '../uploads/packingLists');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// 配置文件上传
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    // 对原始文件名进行解码
    const originalName = Buffer.from(file.originalname, 'latin1').toString('utf8');
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + '-' + originalName);
  }
});

const upload = multer({ 
  storage,
  fileFilter: (req, file, cb) => {
    // 只允许上传 Excel 文件
    if (file.mimetype === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        file.mimetype === 'application/vnd.ms-excel') {
      cb(null, true);
    } else {
      cb(new Error('只支持 Excel 文件格式 (.xlsx, .xls)'));
    }
  }
});

// 获取装箱单列表
router.get('/', async (req, res) => {
  try {
    const { page = 1, pageSize = 10, storeName, type } = req.query;
    const query = {};
    
    if (storeName) {
      query.storeName = new RegExp(storeName, 'i');
    }
    if (type) {
      query.type = type;
    }

    console.log('查询条件:', query);
    console.log('分页参数:', { page, pageSize });

    const total = await PackingList.countDocuments(query);
    const items = await PackingList.find(query)
      .sort({ createdAt: -1 })
      .skip((parseInt(page) - 1) * parseInt(pageSize))
      .limit(parseInt(pageSize))
      .lean();

    console.log('查询结果:', { total, itemsCount: items.length });

    res.json({
      items,
      pagination: {
        total,
        current: parseInt(page),
        pageSize: parseInt(pageSize)
      }
    });
  } catch (error) {
    console.error('获取装箱单列表时出错:', error);
    res.status(500).json({ 
      message: '获取列表失败', 
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

// 导入装箱单
router.post('/import', auth, upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ 
        message: '请选择要导入的文件',
        error: 'No file uploaded'
      });
    }

    // 对文件名进行解码
    const originalName = Buffer.from(req.file.originalname, 'latin1').toString('utf8');
    console.log('原始文件名:', originalName);

    // 从文件名中提取店铺名称
    const storeNameMatch = originalName.match(/^(.+?)海运ERP\.xlsx?$/i);
    if (!storeNameMatch) {
      throw new Error('文件命名格式不正确，应为：{店铺名}海运ERP.xlsx');
    }

    const storeName = storeNameMatch[1].trim();
    if (!storeName) {
      throw new Error('店铺名称不能为空');
    }

    console.log('提取的店铺名称:', storeName);

    const workbook = xlsx.readFile(req.file.path);
    
    // 跳过"常用箱规"sheet
    const sheets = workbook.SheetNames.filter(name => name !== '常用箱规');
    if (sheets.length === 0) {
      throw new Error('Excel文件中没有找到有效的工作表');
    }

    console.log('找到工作表:', sheets);
    const results = [];
    
    for (const sheetName of sheets) {
      console.log('处理工作表:', sheetName);
      const worksheet = workbook.Sheets[sheetName];
      
      // 读取表头信息
      const type = worksheet['D1']?.v || '普货';  // 类型
      const totalBoxes = worksheet['B1']?.v || 0;  // 总箱数
      const totalWeight = worksheet['B2']?.v || 0;  // 总重量
      const totalVolume = worksheet['B3']?.v || 0;  // 总体积
      const totalEdgeVolume = worksheet['B4']?.v || 0;  // 总边加一体积
      const totalPieces = worksheet['B6']?.v || 0;  // 总件数
      const totalValue = worksheet['D2']?.v || 0;  // 总价格

      // 处理箱规信息
      const boxSpecs = [];
      let currentCol = 'F';
      while (worksheet[currentCol + '1']) {
        const specs = {
          boxNo: worksheet[currentCol + '7']?.v,
          length: worksheet[currentCol + '1']?.v,
          width: worksheet[String.fromCharCode(currentCol.charCodeAt(0) + 1) + '1']?.v,
          height: worksheet[String.fromCharCode(currentCol.charCodeAt(0) + 2) + '1']?.v,
          weight: worksheet[currentCol + '2']?.v,
          volume: worksheet[currentCol + '3']?.v,
          edgeVolume: worksheet[currentCol + '4']?.v,
          pieces: worksheet[currentCol + '6']?.v
        };
        if (specs.boxNo) {
          boxSpecs.push(specs);
        }
        // 移动到下一个箱子（每个箱子占用3列）
        currentCol = String.fromCharCode(currentCol.charCodeAt(0) + 3);
      }

      // 收集所有SKU
      const skus = new Set();
      let row = 8;
      while (worksheet['B' + row]) {
        const sku = worksheet['B' + row]?.v;
        if (sku) {
          skus.add(sku);
        }
        row++;
      }

      // 检查并创建不存在的SKU
      console.log('检查SKU是否存在:', Array.from(skus));
      const existingProducts = await Product.find({ sku: { $in: Array.from(skus) } });
      const existingSkus = new Set(existingProducts.map(p => p.sku));
      
      // 创建不存在的SKU
      const createPromises = Array.from(skus)
        .filter(sku => !existingSkus.has(sku))
        .map(async (sku) => {
          console.log('创建新SKU:', sku);
          const newProduct = new Product({
            sku,
            name: `待补充(${sku})`,
            chineseName: `待补充(${sku})`,
            type,
            cost: 0,
            freightCost: 0,
            price: 0,
            stock: 0,
            isAutoCreated: true,
            needsCompletion: true
          });
          return newProduct.save();
        });

      await Promise.all(createPromises);
      console.log('完成SKU创建');

      // 处理商品数据（从第8行开始）
      const items = [];
      row = 8;
      while (worksheet['B' + row]) {
        const sku = worksheet['B' + row]?.v;
        const chineseName = worksheet['C' + row]?.v;
        
        if (sku) {
          const boxQuantities = [];
          let totalQuantity = 0;
          
          // 遍历每个箱子的数量
          for (let i = 0; i < boxSpecs.length; i++) {
            const col = String.fromCharCode('F'.charCodeAt(0) + i * 3);
            const quantity = parseInt(worksheet[col + row]?.v) || 0;
            if (quantity > 0) {
              boxQuantities.push({
                boxNo: boxSpecs[i].boxNo.toString(),
                quantity,
                specs: {
                  length: boxSpecs[i].length,
                  width: boxSpecs[i].width,
                  height: boxSpecs[i].height,
                  weight: boxSpecs[i].weight,
                  volume: boxSpecs[i].volume,
                  edgeVolume: boxSpecs[i].edgeVolume
                }
              });
              totalQuantity += quantity;
            }
          }

          if (boxQuantities.length > 0) {
            items.push({
              sku,
              chineseName: chineseName || `待补充(${sku})`,
              quantity: totalQuantity,
              boxQuantities
            });
          }
        }
        row++;
      }

      // 创建装箱单记录
      const packingList = {
        storeName,
        type,
        totalBoxes,
        totalWeight,
        totalVolume,
        totalEdgeVolume,
        totalPieces,
        totalValue,
        items
      };

      console.log('创建装箱单:', packingList);
      const savedPackingList = await PackingList.create(packingList);
      console.log('保存成功，ID:', savedPackingList._id);
      results.push(savedPackingList);
    }

    // 删除临时文件
    fs.unlinkSync(req.file.path);

    res.json({
      message: '导入成功',
      data: results
    });
  } catch (error) {
    console.error('导入装箱单时出错:', error);
    if (req.file) {
      fs.unlinkSync(req.file.path);
    }
    res.status(400).json({ 
      message: '导入失败', 
      error: error.message 
    });
  }
});

// 获取装箱单详情
router.get('/:id', async (req, res) => {
  try {
    const packingList = await PackingList.findById(req.params.id);
    if (!packingList) {
      return res.status(404).json({ message: '装箱单不存在' });
    }
    res.json(packingList);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 更新装箱单状态
router.patch('/:id/status', async (req, res) => {
  try {
    const { status } = req.body;
    const packingList = await PackingList.findByIdAndUpdate(
      req.params.id,
      { status },
      { new: true }
    );
    if (!packingList) {
      return res.status(404).json({ message: '装箱单不存在' });
    }
    res.json(packingList);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 导出装箱单
router.get('/:id/export', async (req, res) => {
  try {
    const packingList = await PackingList.findById(req.params.id)
      .populate('items.product')
      .populate('customer');
    
    if (!packingList) {
      return res.status(404).json({ message: '装箱单未找到' });
    }

    // 设置响应头
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', `attachment; filename=装箱单_${packingList.storeName}_${Date.now()}.xlsx`);

    // 创建工作簿
    const workbook = xlsx.utils.book_new();
    
    // 创建工作表
    const worksheet = xlsx.utils.aoa_to_sheet([
      ['总箱数', packingList.totalBoxes],
      ['总重量', packingList.totalWeight],
      ['总体积', packingList.totalVolume],
      ['总件数', packingList.totalPieces],
      [],
      ['SKU', '中文名', '数量', '箱号', '规格', '重量', '体积']
    ]);

    // 添加商品数据
    const data = [];
    packingList.items.forEach(item => {
      item.boxQuantities.forEach(bq => {
        data.push([
          item.sku,
          item.chineseName || '',
          bq.quantity,
          bq.boxNo,
          `${bq.specs.length}×${bq.specs.width}×${bq.specs.height}`,
          bq.specs.weight,
          bq.specs.volume
        ]);
      });
    });

    // 将数据添加到工作表
    xlsx.utils.sheet_add_aoa(worksheet, data, { origin: 6 });

    // 将工作表添加到工作簿
    xlsx.utils.book_append_sheet(workbook, worksheet, '装箱单');

    // 生成 Excel 文件
    const excelBuffer = xlsx.write(workbook, { type: 'buffer', bookType: 'xlsx' });

    // 发送文件
    res.send(excelBuffer);
  } catch (error) {
    console.error('导出装箱单时出错:', error);
    res.status(500).json({ message: '导出失败', error: error.message });
  }
});

// 批量导出装箱单
router.post('/batch-download', async (req, res) => {
  try {
    const { ids } = req.body;
    if (!ids || !Array.isArray(ids) || ids.length === 0) {
      return res.status(400).json({ message: '请选择要导出的装箱单' });
    }

    const packingLists = await PackingList.find({ _id: { $in: ids } });
    if (packingLists.length === 0) {
      return res.status(404).json({ message: '未找到要导出的装箱单' });
    }

    // 创建工作簿
    const workbook = xlsx.utils.book_new();

    // 为每个装箱单创建一个工作表
    packingLists.forEach(packingList => {
      const worksheet = xlsx.utils.aoa_to_sheet([
        ['总箱数', packingList.totalBoxes],
        ['总重量', packingList.totalWeight],
        ['总体积', packingList.totalVolume],
        ['总件数', packingList.totalPieces],
        [],
        ['SKU', '中文名', '数量', '箱号', '规格', '重量', '体积']
      ]);

      const data = [];
      packingList.items.forEach(item => {
        item.boxQuantities.forEach(bq => {
          data.push([
            item.sku,
            item.chineseName || '',
            bq.quantity,
            bq.boxNo,
            `${bq.specs.length}×${bq.specs.width}×${bq.specs.height}`,
            bq.specs.weight,
            bq.specs.volume
          ]);
        });
      });

      xlsx.utils.sheet_add_aoa(worksheet, data, { origin: 6 });
      xlsx.utils.book_append_sheet(workbook, worksheet, `${packingList.storeName}`);
    });

    // 生成 Excel 文件
    const excelBuffer = xlsx.write(workbook, { type: 'buffer', bookType: 'xlsx' });

    // 设置响应头
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', `attachment; filename=装箱单批量导出_${Date.now()}.xlsx`);

    // 发送文件
    res.send(excelBuffer);
  } catch (error) {
    console.error('批量导出装箱单时出错:', error);
    res.status(500).json({ message: '批量导出失败', error: error.message });
  }
});

// 删除装箱单
router.delete('/:id', async (req, res) => {
  try {
    if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
      return res.status(400).json({ message: '无效的ID格式' });
    }

    const packingList = await PackingList.findByIdAndDelete(req.params.id);
    if (!packingList) {
      return res.status(404).json({ message: '装箱单不存在' });
    }
    res.json({ message: '删除成功', data: packingList });
  } catch (error) {
    console.error('删除装箱单时出错:', error);
    res.status(500).json({ message: '删除失败', error: error.message });
  }
});

// 批量删除装箱单
router.delete('/', async (req, res) => {
  try {
    const result = await PackingList.deleteMany({});
    if (result.deletedCount === 0) {
      return res.status(404).json({ message: '没有找到要删除的装箱单' });
    }
    res.json({ 
      message: `成功删除 ${result.deletedCount} 个装箱单`,
      data: { deletedCount: result.deletedCount }
    });
  } catch (error) {
    console.error('批量删除装箱单时出错:', error);
    res.status(500).json({ message: '批量删除失败', error: error.message });
  }
});

module.exports = router; 