const express = require('express');
const router = express.Router();
const multer = require('multer');
const xlsx = require('xlsx');
const fs = require('fs');
const path = require('path');
const PackingList = require('../models/PackingList');
const Product = require('../models/Product');

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
    // 解码文件名
    const originalName = decodeURIComponent(escape(file.originalname));
    // 保留原始文件名，但确保文件名是唯一的
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
    const { page = 1, pageSize = 10, storeName, type, status, startDate, endDate } = req.query;
    let query = {};

    if (storeName) {
      query.storeName = new RegExp(storeName, 'i');
    }
    if (type) {
      query.type = type;
    }
    if (status) {
      query.status = status;
    }
    if (startDate || endDate) {
      query.createdAt = {};
      if (startDate) {
        query.createdAt.$gte = new Date(startDate);
      }
      if (endDate) {
        query.createdAt.$lte = new Date(endDate);
      }
    }

    const skip = (parseInt(page) - 1) * parseInt(pageSize);
    const total = await PackingList.countDocuments(query);
    const packingLists = await PackingList.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(pageSize));

    res.json({
      data: {
        items: packingLists,
        pagination: {
          total,
          page: parseInt(page),
          pageSize: parseInt(pageSize)
        }
      }
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 导入装箱单
router.post('/import', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: '请上传文件' });
    }

    // 解码文件名并提取店铺名称
    const originalName = decodeURIComponent(escape(req.file.originalname));
    const storeName = PackingList.extractStoreNameFromFileName(originalName);

    const workbook = xlsx.readFile(req.file.path);
    const worksheet = workbook.Sheets[workbook.SheetNames[0]];

    // 读取装箱单头部信息
    const type = worksheet['D1']?.v || '普货';
    const totalBoxes = Number(worksheet['B1']?.v) || 0;
    const totalWeight = Number(worksheet['B2']?.v) || 0;
    const totalVolume = Number(worksheet['B3']?.v) || 0;
    const totalPieces = Number(worksheet['B6']?.v) || 0;
    const totalValue = Number(worksheet['D2']?.v) || 0;

    if (!totalBoxes || !totalWeight || !totalVolume || !totalPieces || !totalValue) {
      throw new Error('装箱单头部信息不完整，请检查B1(总箱数)、B2(总重量)、B3(总体积)、B6(总件数)、D2(总价值)等单元格');
    }

    // 读取箱子规格信息
    const boxes = [];
    let currentCol = 'F';
    
    // 检查是否存在箱规数据
    while (true) {
      // 检查是否有箱规数据（通过检查长度是否存在）
      const lengthCell = worksheet[currentCol + '1'];
      if (!lengthCell || !lengthCell.v) {
        break; // 如果没有长度数据，说明没有更多箱子了
      }

      const nextCol = String.fromCharCode(currentCol.charCodeAt(0) + 1);
      const nextNextCol = String.fromCharCode(currentCol.charCodeAt(0) + 2);
      
      try {
        // 读取长宽高
        const length = worksheet[currentCol + '1']?.v;
        const width = worksheet[nextCol + '1']?.v;
        const height = worksheet[nextNextCol + '1']?.v;
        
        if (!length || !width || !height) {
          throw new Error(`箱规数据不完整：${currentCol}列的长宽高数据缺失`);
        }

        // 读取其他规格信息
        const weight = worksheet[currentCol + '2']?.v;  // 箱重
        const volume = worksheet[currentCol + '3']?.v;  // 体积
        const edgeVolume = worksheet[currentCol + '4']?.v;  // 单边+1体积
        const totalPieces = worksheet[currentCol + '6']?.v;  // 该箱总件数
        const boxNo = worksheet[currentCol + '7']?.v;  // 箱号

        if (!weight || !volume || !edgeVolume || !totalPieces || !boxNo) {
          throw new Error(`箱规数据不完整：${currentCol}列缺少必要的规格信息`);
        }

        boxes.push({
          boxNo: boxNo.toString(),
          specs: {
            length: Number(length),
            width: Number(width),
            height: Number(height),
            weight: Number(weight),
            volume: Number(volume),
            edgeVolume: Number(edgeVolume),
            totalPieces: Number(totalPieces)
          }
        });

        // 移动到下一个箱子（每个箱子占3列）
        currentCol = String.fromCharCode(currentCol.charCodeAt(0) + 3);
      } catch (error) {
        console.error(`读取箱规数据时出错 (列 ${currentCol}):`, error);
        throw new Error(`读取箱规数据时出错：${error.message}`);
      }
    }

    if (boxes.length === 0) {
      throw new Error('未找到有效的箱规数据');
    }

    console.log('成功读取箱规数据:', boxes);

    // 读取产品信息
    const items = [];
    let row = 8;
    while (worksheet['B' + row]) {
      try {
        const skuCell = worksheet['B' + row];
        const chineseNameCell = worksheet['C' + row];
        
        if (!skuCell || !skuCell.v) {
          break; // 如果没有SKU，说明数据已经结束
        }

        const sku = skuCell.v;
        const chineseName = chineseNameCell?.v;
        const boxQuantities = [];

        // 读取每个箱子的数量
        for (let i = 0; i < boxes.length; i++) {
          const box = boxes[i];
          const col = String.fromCharCode('F'.charCodeAt(0) + i * 3); // 每个箱子间隔3列
          const quantityCell = worksheet[col + row];
          
          if (quantityCell && quantityCell.v !== undefined && quantityCell.v !== null) {
            const quantity = Number(quantityCell.v);
            if (!isNaN(quantity) && quantity > 0) {
              boxQuantities.push({
                boxNo: box.boxNo,
                quantity: quantity,
                specs: box.specs
              });
            }
          }
        }

        // 计算总数量
        const totalQuantity = boxQuantities.reduce((sum, bq) => sum + bq.quantity, 0);

        if (totalQuantity > 0) {
          items.push({
            sku,
            chineseName,
            quantity: totalQuantity,
            boxQuantities
          });
        }

        row++;
      } catch (error) {
        console.error(`处理第 ${row} 行数据时出错:`, error);
        throw new Error(`处理第 ${row} 行数据时出错: ${error?.message || '未知错误'}`);
      }
    }

    if (items.length === 0) {
      throw new Error('未找到有效的商品数据');
    }

    console.log('成功读取商品数据:', items);

    // 创建装箱单
    const packingList = new PackingList({
      storeName,
      type,
      status: 'pending',
      totalBoxes,
      totalWeight,
      totalVolume,
      totalPieces,
      totalValue,
      items,
      remarks: `从Excel导入于 ${new Date().toLocaleString()}`
    });

    // 先创建不存在的SKU
    const distinctSkus = [...new Set(items.map(item => item.sku))];
    const existingProducts = await Product.find({ sku: { $in: distinctSkus } });
    const existingSkus = existingProducts.map(p => p.sku);
    
    const newSkus = distinctSkus.filter(sku => !existingSkus.includes(sku));
    if (newSkus.length > 0) {
      console.log('需要创建的新SKU:', newSkus);
      const newProducts = newSkus.map(sku => {
        const item = items.find(i => i.sku === sku);
        return {
          sku,
          name: `待补充(${sku})`,
          chineseName: item.chineseName || `待补充(${sku})`,
          type,
          price: 0,
          stock: 0,
          isAutoCreated: true,
          needsCompletion: true
        };
      });
      
      await Product.insertMany(newProducts);
      console.log('新SKU创建完成');
    }

    try {
      await packingList.save();
      console.log('装箱单保存成功:', {
        storeName,
        type,
        totalBoxes,
        totalValue,
        itemsCount: items.length
      });
      res.json({ message: '装箱单导入成功' });
    } catch (error) {
      console.error('保存装箱单时出错:', error);
      if (error.name === 'ValidationError') {
        const validationErrors = Object.keys(error.errors).map(key => 
          `${key}: ${error.errors[key].message}`
        ).join('; ');
        throw new Error(`数据验证失败: ${validationErrors}`);
      }
      throw error;
    }

  } catch (error) {
    console.error('导入装箱单时出错:', error);
    const errorMessage = error?.message || (typeof error === 'string' ? error : '导入装箱单时发生未知错误');
    res.status(400).json({ message: errorMessage });
  } finally {
    // 删除临时文件
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
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

// 删除装箱单
router.delete('/:id', async (req, res) => {
  try {
    const packingList = await PackingList.findByIdAndDelete(req.params.id);
    if (!packingList) {
      return res.status(404).json({ message: '装箱单不存在' });
    }
    res.json({ message: '删除成功' });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

module.exports = router; 