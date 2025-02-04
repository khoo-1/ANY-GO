const mongoose = require('mongoose');

const operationLogSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  username: {
    type: String,
    required: true
  },
  module: {
    type: String,
    enum: ['products', 'packingLists', 'users', 'system'],
    required: true
  },
  action: {
    type: String,
    enum: ['create', 'update', 'delete', 'read', 'import', 'export', 'backup'],
    required: true
  },
  description: {
    type: String,
    required: true
  },
  details: {
    type: mongoose.Schema.Types.Mixed
  },
  ip: String,
  userAgent: String,
  status: {
    type: String,
    enum: ['success', 'failure'],
    default: 'success'
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// 创建索引
operationLogSchema.index({ createdAt: -1 });
operationLogSchema.index({ userId: 1, createdAt: -1 });
operationLogSchema.index({ module: 1, action: 1, createdAt: -1 });

module.exports = mongoose.model('OperationLog', operationLogSchema); 