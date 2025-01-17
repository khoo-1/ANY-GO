const mongoose = require('mongoose');

const stockHistorySchema = new mongoose.Schema({
  product: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Product',
    required: true
  },
  type: {
    type: String,
    enum: ['入库', '出库', '调整'],
    required: true
  },
  quantity: {
    type: Number,
    required: true
  },
  previousStock: Number,
  currentStock: Number,
  reason: String,
  operator: String,
  date: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('StockHistory', stockHistorySchema); 