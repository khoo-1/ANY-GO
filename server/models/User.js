const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  password: {
    type: String,
    required: true
  },
  role: {
    type: String,
    enum: ['admin', 'manager', 'operator'],
    default: 'operator'
  },
  permissions: [{
    type: String,
    enum: [
      'products:read',
      'products:write',
      'products:delete',
      'packingLists:read',
      'packingLists:write',
      'packingLists:delete',
      'users:read',
      'users:write',
      'users:delete',
      'system:backup'
    ]
  }],
  status: {
    type: String,
    enum: ['active', 'inactive'],
    default: 'active'
  },
  lastLoginAt: Date,
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: Date
});

// 密码加密中间件
userSchema.pre('save', async function(next) {
  if (this.isModified('password')) {
    this.password = await bcrypt.hash(this.password, 10);
  }
  this.updatedAt = new Date();
  next();
});

// 验证密码方法
userSchema.methods.comparePassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// 默认权限设置
userSchema.methods.getDefaultPermissions = function() {
  switch (this.role) {
    case 'admin':
      return [
        'products:read', 'products:write', 'products:delete',
        'packingLists:read', 'packingLists:write', 'packingLists:delete',
        'users:read', 'users:write', 'users:delete',
        'system:backup'
      ];
    case 'manager':
      return [
        'products:read', 'products:write',
        'packingLists:read', 'packingLists:write',
        'users:read'
      ];
    case 'operator':
      return [
        'products:read',
        'packingLists:read'
      ];
    default:
      return [];
  }
};

module.exports = mongoose.model('User', userSchema); 