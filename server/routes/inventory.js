const express = require('express');
const router = express.Router();
const Product = require('../models/Product');
const StockHistory = require('../models/StockHistory');

// 获取所有产品库存
router.get('/products', async (req, res) => {
  try {
    const products = await Product.find().select('sku name stock alertThreshold');
    res.json(products);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 更新产品库存
router.post('/update-stock', async (req, res) => {
  try {
    const { productId, type, quantity, reason, operator } = req.body;
    
    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({ message: '产品不存在' });
    }

    const previousStock = product.stock;
    let currentStock;

    if (type === '入库') {
      currentStock = previousStock + quantity;
    } else if (type === '出库') {
      if (previousStock < quantity) {
        return res.status(400).json({ message: '库存不足' });
      }
      currentStock = previousStock - quantity;
    }

    // 更新产品库存
    product.stock = currentStock;
    product.updatedAt = new Date();
    await product.save();

    // 记录库存变动历史
    const stockHistory = new StockHistory({
      product: productId,
      type,
      quantity,
      previousStock,
      currentStock,
      reason,
      operator
    });
    await stockHistory.save();

    res.json({ 
      message: '库存更新成功',
      currentStock,
      stockHistory 
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 获取库存预警产品
router.get('/low-stock', async (req, res) => {
  try {
    const lowStockProducts = await Product.find({
      $expr: {
        $lte: ['$stock', '$alertThreshold']
      }
    });
    res.json(lowStockProducts);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 获取产品库存历史记录
router.get('/history/:productId', async (req, res) => {
  try {
    const history = await StockHistory.find({ product: req.params.productId })
      .sort({ date: -1 })
      .populate('product', 'sku name');
    res.json(history);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

module.exports = router; 