const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const path = require('path');
require('dotenv').config();
const apiRoutes = require('./routes/api');
const backupService = require('./services/backupService');
const scheduleService = require('./services/scheduleService');

const app = express();

// CORS 配置
app.use(cors({
  origin: '*',  // 允许所有来源访问
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
  allowedHeaders: [
    'Content-Type',
    'Authorization',
    'X-Requested-With',
    'Accept',
    'Origin',
    'Access-Control-Allow-Headers',
    'Access-Control-Request-Method',
    'Access-Control-Request-Headers'
  ],
  credentials: true,
  exposedHeaders: ['Content-Length', 'X-Total-Count']
}));

// 中间件
app.use(express.json());
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

app.use('/api', apiRoutes);

const HOST = process.env.HOST || '0.0.0.0';
const PORT = process.env.PORT || 5000;

// 连接数据库并启动服务器
mongoose.connect(MONGODB_URI)
  .then(async () => {
    console.log('数据库连接成功');
    
    // 初始化备份目录
    await backupService.init();
    console.log('备份目录初始化完成');

    // 初始化定时任务
    await scheduleService.init();
    console.log('定时任务初始化完成');

    // 启动服务器
    app.listen(PORT, HOST, () => {
      console.log(`服务器运行在 http://${HOST}:${PORT}`);
      console.log(`局域网访问地址: http://192.168.110.13:${PORT}`);
    });
  })
  .catch(error => {
    console.error('数据库连接失败:', error);
    process.exit(1);
  });

// 优雅关闭
process.on('SIGTERM', async () => {
  console.log('收到 SIGTERM 信号，准备关闭服务...');
  
  // 取消所有定时任务
  scheduleService.cancelAllJobs();
  
  // 关闭数据库连接
  await mongoose.connection.close();
  console.log('数据库连接已关闭');
  
  process.exit(0);
}); 