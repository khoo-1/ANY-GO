# ANY-GO 跨境电商管理系统

一个现代化的跨境电商管理系统，基于 React + Node.js + MongoDB 技术栈，专注于 SKU 和装箱单管理。

## ✨ 功能特性

- 📦 SKU 管理
  - SKU 唯一性验证
  - SKU 格式验证
  - SKU 批量导入
  - 自动创建缺失 SKU
- 📋 装箱单管理
  - Excel 导入功能
  - 自动提取店铺信息
  - 类型验证（普货/纺织/混装）
  - 汇总信息显示
- 🎯 产品信息维护
  - 基本信息：SKU、名称、中文名、描述、类别
  - 类型信息：普货/纺织/混装
  - 价格信息：售价、成本价
  - 图片管理：支持多图
- 📊 数据导入导出
  - Excel 模板下载
  - 批量导入验证
  - 导出筛选结果

## 🚀 快速开始

### 环境要求

- Node.js >= 17
- MongoDB >= 5.0
- npm >= 9.0

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/yourusername/ANY-GO.git
cd ANY-GO
```

2. 安装依赖
```bash
# 安装后端依赖
cd server
npm install

# 安装前端依赖
cd ../client
npm install
```

3. 配置环境变量
```bash
# 后端配置 (server/.env)
MONGODB_URI=mongodb://localhost:27017/any-go
PORT=5000

# 前端配置 (client/.env)
REACT_APP_API_URL=http://localhost:5000
```

4. 启动服务
```bash
# 启动后端服务
cd server
npm run dev

# 新开终端，启动前端服务
cd client
npm start
```

访问 http://localhost:3000 即可看到应用界面

## 🏗️ 技术栈

### 前端
- React 17 + TypeScript
- Ant Design 4.x
- Axios + React Router Dom
- Excel 文件处理

### 后端
- Node.js + Express
- MongoDB + Mongoose
- Excel 解析
- 文件上传处理

## 📖 项目规范

详细规范请查看 [PROJECT_SPEC.md](./PROJECT_SPEC.md)

### 数据规则
- SKU 格式验证
- 装箱单 Excel 格式要求
- 产品类型规则（普货/纺织/混装）

### 开发规范
- TypeScript 类型检查
- ESLint + Prettier 代码格式化
- Git Commit 规范
- 组件文档

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

[MIT License](./LICENSE)

## 👥 维护者

- 作者：[Your Name]
- 邮箱：[Your Email]
- GitHub：[Your GitHub]

---

如果这个项目对你有帮助，欢迎 star ⭐️
