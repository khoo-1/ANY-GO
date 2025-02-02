const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const path = require('path');
require('dotenv').config();

const app = express();

// 中间件
app.use(cors());
app.use(express.json());

// 静态文件服务
app.use('/uploads', express.static('uploads'));

// 数据库连接配置
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/any-go';
const connectOptions = {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
};

// 数据库连接函数
const connectDB = async (retryCount = 0) => {
  const MAX_RETRIES = 3;
  try {
    await mongoose.connect(MONGODB_URI, connectOptions);
    console.log('数据库连接成功');
  } catch (error) {
    console.error('数据库连接错误:', error);
    if (retryCount < MAX_RETRIES) {
      console.log(`尝试重新连接... (${retryCount + 1}/${MAX_RETRIES})`);
      setTimeout(() => connectDB(retryCount + 1), 3000);
    }
  }
};

// 连接数据库
connectDB();

// 监听数据库连接事件
mongoose.connection.on('disconnected', () => {
  console.log('数据库连接断开，尝试重新连接...');
  connectDB();
});

// API 健康检查
app.get('/', (req, res) => {
  res.json({ 
    message: 'API 运行正常',
    dbStatus: mongoose.connection.readyState === 1 ? '已连接' : '未连接'
  });
});

// 路由
const inventoryRoutes = require('./routes/inventory');
const productRoutes = require('./routes/products');
const packingListRoutes = require('./routes/packingLists');

app.use('/api/inventory', inventoryRoutes);
app.use('/api/products', productRoutes);
app.use('/api/packing-lists', packingListRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`服务器运行在端口 ${PORT}`);
}); 