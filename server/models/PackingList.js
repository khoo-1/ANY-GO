const mongoose = require('mongoose');

const boxSpecsSchema = new mongoose.Schema({
  length: Number,
  width: Number,
  height: Number,
  weight: Number,
  volume: Number,
  edgeVolume: Number,
  totalPieces: Number
}, { _id: false });

const boxQuantitySchema = new mongoose.Schema({
  boxNo: {
    type: String,
    required: true
  },
  quantity: {
    type: Number,
    required: true,
    min: 1
  },
  specs: {
    type: boxSpecsSchema,
    required: true
  }
}, { _id: false });

const packingListItemSchema = new mongoose.Schema({
  sku: {
    type: String,
    required: true,
    ref: 'Product'
  },
  quantity: {
    type: Number,
    required: true,
    min: 1
  },
  boxQuantities: {
    type: [boxQuantitySchema],
    required: true,
    validate: {
      validator: function(v) {
        return v.length > 0;
      },
      message: '每个商品至少需要在一个箱子中有数量'
    }
  }
});

const packingListSchema = new mongoose.Schema({
  storeName: {
    type: String,
    required: true,
    trim: true
  },
  type: {
    type: String,
    enum: ['普货', '纺织', '混装'],
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'approved'],
    default: 'pending'
  },
  totalBoxes: {
    type: Number,
    required: true
  },
  totalWeight: {
    type: Number,
    required: true
  },
  totalVolume: {
    type: Number,
    required: true
  },
  totalPieces: {
    type: Number,
    required: true
  },
  totalValue: {
    type: Number,
    required: true
  },
  items: [packingListItemSchema],
  remarks: String,
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
packingListSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

// 自动从文件名提取店铺信息
packingListSchema.statics.extractStoreNameFromFileName = function(fileName) {
  if (!fileName) {
    throw new Error('文件名不能为空');
  }

  console.log('正在处理文件名:', fileName); // 添加日志

  // 移除文件扩展名
  const nameWithoutExt = fileName.replace(/\.xlsx?$/i, '');
  console.log('移除扩展名后:', nameWithoutExt); // 添加日志
  
  // 检查文件名格式
  const suffix = '海运ERP';
  if (!nameWithoutExt.endsWith(suffix)) {
    throw new Error(`文件名格式错误，必须以"海运ERP"结尾，当前文件名：${nameWithoutExt}`);
  }

  // 提取店铺名称（移除末尾的"海运ERP"）
  const storeName = nameWithoutExt.substring(0, nameWithoutExt.length - suffix.length);
  console.log('提取的店铺名称:', storeName); // 添加日志

  if (!storeName) {
    throw new Error('无法从文件名中提取店铺名称，请确保文件名格式为："{店铺名}海运ERP.xlsx"');
  }

  return storeName;
};

// 验证商品类型是否匹配
packingListSchema.methods.validateProductTypes = async function() {
  const Product = mongoose.model('Product');
  const distinctSkus = [...new Set(this.items.map(item => item.sku))];
  
  console.log('正在验证商品类型...');
  console.log('装箱单类型:', this.type);
  console.log('需要验证的SKU:', distinctSkus);

  const products = await Product.find({ sku: { $in: distinctSkus } });
  console.log('找到的商品:', products.map(p => ({ sku: p.sku, type: p.type })));

  const productTypeMap = products.reduce((map, product) => {
    map[product.sku] = product.type;
    return map;
  }, {});

  if (this.type === '混装') {
    console.log('装箱单类型为混装，跳过类型验证');
    return true;
  }

  const invalidItems = this.items.filter(item => {
    const productType = productTypeMap[item.sku];
    return productType !== this.type;
  });

  if (invalidItems.length > 0) {
    console.log('类型不匹配的商品:', invalidItems.map(item => ({
      sku: item.sku,
      expectedType: this.type,
      actualType: productTypeMap[item.sku]
    })));
    throw new Error(`以下商品类型与装箱单类型(${this.type})不匹配：\n${
      invalidItems.map(item => `SKU: ${item.sku}, 商品类型: ${productTypeMap[item.sku] || '未知'}`).join('\n')
    }`);
  }

  console.log('商品类型验证通过');
  return true;
};

module.exports = mongoose.model('PackingList', packingListSchema); 