const mongoose = require('mongoose');

const backupSchema = new mongoose.Schema({
  filename: {
    type: String,
    required: true
  },
  size: {
    type: Number,
    required: true
  },
  type: {
    type: String,
    enum: ['full', 'products', 'packingLists'],
    default: 'full'
  },
  status: {
    type: String,
    enum: ['pending', 'completed', 'failed'],
    default: 'pending'
  },
  path: {
    type: String,
    required: true
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  description: String,
  error: String,
  createdAt: {
    type: Date,
    default: Date.now
  },
  completedAt: Date
});

// 创建索引
backupSchema.index({ createdAt: -1 });
backupSchema.index({ type: 1, createdAt: -1 });
backupSchema.index({ status: 1, createdAt: -1 });

module.exports = mongoose.model('Backup', backupSchema); 