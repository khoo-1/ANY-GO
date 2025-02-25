# ANY-GO 跨境电商平台

ANY-GO 是一个跨境电商团队协作平台，旨在帮助跨境电商团队更高效地管理产品、库存、装箱单和利润分析。

## 技术栈

### 前端
- React + TypeScript
- Vite 构建工具
- Ant Design 组件库
- React Router 路由管理
- Zustand 状态管理
- Axios HTTP 客户端

### 后端
- Python FastAPI 框架
- PostgreSQL 数据库
- SQLAlchemy ORM
- JWT 认证
- Alembic 数据库迁移

## 功能特性

- 用户认证与权限管理
- 产品管理
- 装箱单管理
- 库存管理
- 利润分析
- 数据导入/导出

## 开发环境设置

### 前端

1. 安装依赖
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

### 后端

1. 创建虚拟环境
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 设置环境变量
创建 `.env` 文件在 `backend` 目录下，并添加以下内容：
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/any_go
SECRET_KEY=your-secret-key-here-please-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173
DEBUG=true
```

4. 初始化数据库
```bash
python init_db.py
python init_users.py
```

5. 启动服务器
```bash
python main.py
```

## API 文档

启动后端服务器后，可以通过以下URL访问API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 默认用户

系统初始化后会创建两个默认用户：

1. 管理员
   - 用户名: admin
   - 密码: admin123
   - 权限: 所有功能的读写权限

2. 普通用户
   - 用户名: user
   - 密码: user123
   - 权限: 产品、装箱单、利润和库存的只读权限

## 项目结构

```
any-go/
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── components/      # 组件
│   │   ├── pages/           # 页面
│   │   ├── services/        # API服务
│   │   ├── stores/          # 状态管理
│   │   └── utils/           # 工具函数
│   ├── public/              # 静态资源
│   └── package.json         # 依赖配置
│
├── backend/                 # 后端代码
│   ├── app/                 # 应用代码
│   │   ├── routers/         # API路由
│   │   ├── models.py        # 数据模型
│   │   └── database.py      # 数据库配置
│   ├── main.py              # 主程序
│   ├── init_db.py           # 数据库初始化
│   ├── init_users.py        # 用户初始化
│   └── requirements.txt     # 依赖配置
│
└── README.md                # 项目说明
```

## 许可证

MIT
