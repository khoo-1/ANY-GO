# ANY-GO 跨境电商团队协作平台

## 项目简介
ANY-GO 是一个专为跨境电商团队设计的协作平台，提供产品管理、库存管理、装箱单管理、利润分析等功能，帮助团队提高工作效率和决策能力。

## 技术栈

### 后端
- FastAPI - 高性能的 Python Web 框架
- PostgreSQL - 关系型数据库
- SQLAlchemy - ORM 框架
- Pydantic - 数据验证
- Python 3.8+ - 编程语言

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- TypeScript - 类型系统
- Element Plus - UI 组件库
- ECharts - 图表库
- Vite - 构建工具
- Pinia - 状态管理
- Vue Router 4 - 路由管理

## 主要功能

1. **用户管理**
   - 用户认证
   - 权限控制
   - 用户信息管理

2. **产品管理**
   - 产品信息维护
   - SKU管理
   - 产品分类
   - 批量导入/导出

3. **库存管理**
   - 库存记录
   - 入库/出库
   - 库存盘点
   - 库存预警
   - 库存分析

4. **装箱单管理**
   - 装箱单创建/编辑
   - 装箱明细
   - 箱号管理
   - 批量导入/导出
   - 打印功能

5. **利润分析**
   - 利润概览
   - 商品利润分析
   - 品类利润分析
   - 多维度分析

6. **系统管理**
   - 操作日志
   - 数据备份/恢复
   - 系统设置

## 快速开始

### 环境要求
- Python 3.8+
- PostgreSQL 12+
- Node.js 14+

### 后端启动
1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

2. 安装依赖
```bash
cd any-go-python/backend
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

4. 启动服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动
1. 安装依赖
```bash
cd client
npm install
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置API地址等信息
```

3. 开发环境启动
```bash
npm run dev
```

4. 生产环境构建
```bash
npm run build
```

## 项目结构
```
any-go/
├── any-go-python/          # 后端项目
│   ├── backend/
│   │   ├── app/           # 应用代码
│   │   ├── tests/         # 测试代码
│   │   └── requirements.txt
│   └── README.md
├── client/                # 前端项目（Vue 3 + TypeScript）
│   ├── src/
│   │   ├── components/   # 组件
│   │   ├── views/       # 页面视图
│   │   ├── stores/      # Pinia 状态管理
│   │   ├── api/         # API 接口
│   │   ├── utils/       # 工具函数
│   │   ├── router/      # 路由配置
│   │   └── types/       # TypeScript 类型定义
│   ├── public/          # 静态资源
│   └── package.json
├── PROJECT_SPEC.md       # 项目规格说明
└── README.md            # 项目说明
```

## 贡献指南
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证
本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情
