const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function checkPrerequisites() {
  try {
    // 检查 Node.js
    execSync('node --version');
    console.log('✓ Node.js 已安装');
  } catch (e) {
    console.error('✗ 请先安装 Node.js');
    process.exit(1);
  }

  try {
    // 检查 MongoDB
    execSync('mongod --version');
    console.log('✓ MongoDB 已安装');
  } catch (e) {
    console.error('✗ 请先安装 MongoDB');
    process.exit(1);
  }
}

function setupProject() {
  // 创建必要的目录
  const dirs = [
    'client/src/components',
    'client/src/pages',
    'client/src/utils',
    'client/src/types',
    'server/routes',
    'server/models',
    'server/uploads/products'
  ];

  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });

  // 创建配置文件
  const configs = {
    'client/.env': `SKIP_PREFLIGHT_CHECK=true
GENERATE_SOURCEMAP=false
REACT_APP_API_URL=http://localhost:5000`,
    'server/.env': `MONGODB_URI=mongodb://localhost:27017/cross-border-ecommerce
PORT=5000`
  };

  Object.entries(configs).forEach(([file, content]) => {
    fs.writeFileSync(file, content);
  });

  // 安装依赖
  console.log('正在安装服务器依赖...');
  execSync('cd server && npm install', { stdio: 'inherit' });

  console.log('正在安装客户端依赖...');
  execSync('cd client && npm install', { stdio: 'inherit' });

  console.log('✓ 项目设置完成');
}

checkPrerequisites();
setupProject(); 