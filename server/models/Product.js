const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  sku: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  chineseName: {
    type: String,
    trim: true,
    default: function() {
      return `待补充(${this.sku})`;
    }
  },
  description: String,
  category: {
    type: String,
    default: '未分类'
  },
  type: {
    type: String,
    enum: ['普货', '纺织', '混装'],
    required: true
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  cost: {
    type: Number,
    min: 0,
    default: 0
  },
  stock: {
    type: Number,
    default: 0,
    min: 0
  },
  alertThreshold: {
    type: Number,
    default: 10
  },
  supplier: String,
  images: [{
    type: String
  }],
  status: {
    type: String,
    enum: ['active', 'inactive'],
    default: 'active'
  },
  isAutoCreated: {
    type: Boolean,
    default: false
  },
  needsCompletion: {
    type: Boolean,
    default: false
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// 更新时自动设置 updatedAt
productSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

// SKU 唯一性验证中间件
productSchema.pre('save', async function(next) {
  if (this.isNew || this.isModified('sku')) {
    const exists = await this.constructor.findOne({ sku: this.sku });
    if (exists) {
      next(new Error('SKU已存在'));
    }
  }
  next();
});

module.exports = mongoose.model('Product', productSchema); 