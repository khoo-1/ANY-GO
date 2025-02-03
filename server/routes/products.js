const express = require('express');
const router = express.Router();
const Product = require('../models/Product');
const multer = require('multer');
const path = require('path');
const xlsx = require('xlsx');
const fs = require('fs');

// 配置文件上传
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/products/');
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});

const upload = multer({ storage: storage });

// 获取商品列表
router.get('/', async (req, res) => {
  try {
    const { page = 1, pageSize = 10, keyword, category, status } = req.query;
    let query = {};

    if (keyword) {
      query.$or = [
        { sku: new RegExp(keyword, 'i') },
        { name: new RegExp(keyword, 'i') },
        { supplier: new RegExp(keyword, 'i') }
      ];
    }

    if (category) {
      query.category = category;
    }

    if (status === 'low') {
      query.$expr = { $lte: ['$stock', '$alertThreshold'] };
    } else if (status === 'out') {
      query.stock = 0;
    }

    const skip = (parseInt(page) - 1) * parseInt(pageSize);
    const total = await Product.countDocuments(query);
    const products = await Product.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(pageSize));

    res.json({
      data: {
        items: products,
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

// 创建新商品
router.post('/', upload.array('images', 5), async (req, res) => {
  try {
    const productData = req.body;
    
    // 处理上传的图片
    if (req.files) {
      productData.images = req.files.map(file => `/uploads/products/${file.filename}`);
    }

    const product = new Product(productData);
    await product.save();
    res.status(201).json(product);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

// 更新商品信息
router.put('/:id', upload.array('images', 5), async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;

    // 处理新上传的图片
    if (req.files && req.files.length > 0) {
      const newImages = req.files.map(file => `/uploads/products/${file.filename}`);
      updateData.images = [...(updateData.images || []), ...newImages];
    }

    const product = await Product.findByIdAndUpdate(
      id,
      { ...updateData, updatedAt: new Date() },
      { new: true }
    );

    if (!product) {
      return res.status(404).json({ message: '商品不存在' });
    }

    res.json(product);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

// 删除商品
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const product = await Product.findByIdAndDelete(id);
    
    if (!product) {
      return res.status(404).json({ message: '商品不存在' });
    }

    // TODO: 删除关联的图片文件

    res.json({ message: '商品删除成功' });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 批量导入商品
router.post('/batch', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: '请上传文件' });
    }

    const workbook = xlsx.readFile(req.file.path);
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const data = xlsx.utils.sheet_to_json(worksheet);

    const products = data.map(row => ({
      sku: row['SKU'],
      name: row['商品名称'],
      description: row['描述'],
      category: row['类别'],
      price: Number(row['售价']) || 0,
      cost: Number(row['成本价']) || 0,
      stock: Number(row['库存']) || 0,
      alertThreshold: Number(row['库存预警阈值']) || 10,
      supplier: row['供应商']
    }));

    // 批量插入商品
    await Product.insertMany(products);

    // 删除临时文件
    fs.unlinkSync(req.file.path);

    res.json({ message: '批量导入成功', count: products.length });
  } catch (error) {
    if (req.file) {
      fs.unlinkSync(req.file.path);
    }
    res.status(400).json({ message: error.message });
  }
});

// 下载Excel导入模板
router.get('/template', (req, res) => {
  try {
    // 创建工作簿
    const workbook = xlsx.utils.book_new();
    
    // 创建工作表
    const worksheet = xlsx.utils.aoa_to_sheet([
      ['SKU', '中文名', '类型', '成本价', '头程运费', '备注'],
      ['ABC123456', '示例商品', '普货', '100', '50', 'SKU格式：6-30位大写字母、数字、连字符或下划线'],
      ['DEF789012', '示例纺织品', '纺织', '200', '80', '类型只能是：普货、纺织、混装'],
    ]);

    // 设置列宽
    const colWidths = [
      { wch: 15 },  // SKU
      { wch: 20 },  // 中文名
      { wch: 10 },  // 类型
      { wch: 10 },  // 成本价
      { wch: 10 },  // 头程运费
      { wch: 40 }   // 备注
    ];
    worksheet['!cols'] = colWidths;

    // 添加工作表到工作簿
    xlsx.utils.book_append_sheet(workbook, worksheet, '产品导入模板');

    // 生成文件
    const buffer = xlsx.write(workbook, { type: 'buffer', bookType: 'xlsx' });

    // 设置响应头
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', 'attachment; filename=product_import_template.xlsx');

    // 发送文件
    res.send(buffer);

  } catch (error) {
    console.error('生成模板失败:', error);
    res.status(500).json({ message: '生成模板失败', error: error.message });
  }
});

// 批量导入产品
router.post('/import', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: '请选择要导入的文件' });
    }

    console.log('开始处理导入文件');
    // 读取Excel文件
    const workbook = xlsx.readFile(req.file.path);
    const worksheet = workbook.Sheets[workbook.SheetNames[0]];
    const data = xlsx.utils.sheet_to_json(worksheet);

    // 验证和处理数据
    const results = {
      success: [],
      errors: []
    };

    for (let row of data) {
      try {
        console.log('处理行数据:', row);
        // 数据验证
        if (!row.SKU || !row.中文名 || !row.类型 || !row.成本价 || !row.头程运费) {
          throw new Error('必填字段不能为空');
        }

        // 验证SKU格式
        if (!/^[A-Z0-9\-_]{6,30}$/.test(row.SKU)) {
          throw new Error('SKU格式不正确');
        }

        // 验证类型
        if (!['普货', '纺织', '混装'].includes(row.类型)) {
          throw new Error('无效的类型值');
        }

        // 验证数字字段
        if (isNaN(Number(row.成本价)) || Number(row.成本价) < 0) {
          throw new Error('成本价必须是非负数');
        }
        if (isNaN(Number(row.头程运费)) || Number(row.头程运费) < 0) {
          throw new Error('头程运费必须是非负数');
        }

        // 创建产品对象
        const product = new Product({
          sku: row.SKU,
          chineseName: row.中文名,
          type: row.类型,
          cost: Number(row.成本价),
          freightCost: Number(row.头程运费)
        });

        // 保存产品
        await product.save();
        console.log('保存成功:', row.SKU);
        results.success.push({
          sku: row.SKU,
          message: '导入成功'
        });

      } catch (error) {
        console.error('处理行数据失败:', error);
        results.errors.push({
          sku: row.SKU || '未知SKU',
          error: error.message
        });
      }
    }

    // 删除临时文件
    fs.unlinkSync(req.file.path);

    // 返回结果
    res.json({
      message: `成功导入 ${results.success.length} 条记录，失败 ${results.errors.length} 条`,
      results
    });

  } catch (error) {
    // 删除临时文件
    if (req.file && req.file.path) {
      fs.unlinkSync(req.file.path);
    }
    
    console.error('批量导入失败:', error);
    res.status(500).json({ 
      message: '导入失败', 
      error: error.message 
    });
  }
});

// 导出当前筛选结果
router.get('/export', async (req, res) => {
  try {
    const query = {};
    if (req.query.keyword) {
      query.$or = [
        { sku: new RegExp(req.query.keyword, 'i') },
        { chineseName: new RegExp(req.query.keyword, 'i') }
      ];
    }
    if (req.query.type) {
      query.type = req.query.type;
    }

    const products = await Product.find(query);

    // 创建工作簿
    const workbook = xlsx.utils.book_new();
    
    // 转换数据格式
    const data = products.map(p => ({
      'SKU': p.sku,
      '中文名': p.chineseName,
      '类型': p.type,
      '成本价': p.cost,
      '头程运费': p.freightCost,
      '创建时间': new Date(p.createdAt).toLocaleString(),
      '更新时间': new Date(p.updatedAt).toLocaleString()
    }));

    // 创建工作表
    const worksheet = xlsx.utils.json_to_sheet(data);

    // 设置列宽
    const colWidths = [
      { wch: 15 },  // SKU
      { wch: 20 },  // 中文名
      { wch: 10 },  // 类型
      { wch: 10 },  // 成本价
      { wch: 10 },  // 头程运费
      { wch: 20 },  // 创建时间
      { wch: 20 }   // 更新时间
    ];
    worksheet['!cols'] = colWidths;

    // 添加工作表到工作簿
    xlsx.utils.book_append_sheet(workbook, worksheet, '产品列表');

    // 生成文件
    const buffer = xlsx.write(workbook, { type: 'buffer', bookType: 'xlsx' });

    // 设置响应头
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', 'attachment; filename=products.xlsx');

    // 发送文件
    res.send(buffer);

  } catch (error) {
    console.error('导出失败:', error);
    res.status(500).json({ message: '导出失败', error: error.message });
  }
});

module.exports = router; 