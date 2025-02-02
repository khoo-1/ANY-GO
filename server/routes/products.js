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

module.exports = router; 