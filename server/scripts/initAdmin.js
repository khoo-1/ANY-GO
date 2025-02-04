const mongoose = require('mongoose');
const User = require('../models/User');

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/any-go';

async function initAdmin() {
  try {
    await mongoose.connect(MONGODB_URI);
    console.log('数据库连接成功');

    // 检查是否已存在管理员账户
    const existingAdmin = await User.findOne({ username: 'admin' });
    if (existingAdmin) {
      console.log('管理员账户已存在，正在更新密码...');
      existingAdmin.password = 'admin123';
      await existingAdmin.save();
      console.log('管理员密码已更新');
    } else {
      // 创建新的管理员账户
      const admin = new User({
        username: 'admin',
        password: 'admin123',
        role: 'admin',
        status: 'active'
      });
      
      // 设置管理员权限
      admin.permissions = admin.getDefaultPermissions();
      await admin.save();
      console.log('管理员账户创建成功');
    }

    console.log('初始化完成');
    process.exit(0);
  } catch (error) {
    console.error('初始化失败:', error);
    process.exit(1);
  }
}

initAdmin(); 