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

## 快速启动

我们提供了一个简单的一键启动脚本，可以自动检查和准备环境，并启动前后端服务。

```bash
# Windows
.\start.ps1

# 如果遇到执行策略限制，可以使用以下命令暂时放行
PowerShell -ExecutionPolicy Bypass -File .\start.ps1
```

启动脚本具有以下特性：
- 详细的日志记录（保存在backend目录下）
- 自动检查并创建虚拟环境
- 同时支持 `.venv` 和 `venv` 两种虚拟环境目录
- 数据库自动备份和初始化
- 增强的错误诊断和日志分析

## 开发环境设置

如果您需要手动设置开发环境，请按以下步骤操作：

### 前端

1. 安装依赖
```bash
cd client
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
# 推荐使用 .venv 作为虚拟环境目录名
python -m venv .venv  
# 或者使用标准名称
# python -m venv venv

# 激活虚拟环境
.\.venv\Scripts\activate  # Windows (.venv)
# 或者
# .\venv\Scripts\activate  # Windows (venv)
source .venv/bin/activate  # Linux/Mac (.venv)
# 或者
# source venv/bin/activate  # Linux/Mac (venv)
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
python init_combined.py  # 使用统一初始化脚本
# 或者分开执行
# python init_db.py
# python init_users.py
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

## 虚拟环境说明

本项目支持两种虚拟环境目录结构：
- `.venv`（推荐，遵循 Python 最新推荐实践）
- `venv`（传统方式）

启动脚本会自动检测这两种目录，优先使用 `.venv` 目录。如果您使用自定义的虚拟环境目录名称，需要手动修改启动脚本。

## 项目结构

```
any-go/
├── client/                  # 前端代码
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── utils/           # 工具函数
│   │   ├── types/           # TypeScript 类型定义
│   │   ├── stores/          # 状态管理
│   │   ├── router/          # 路由配置
│   │   ├── assets/          # 静态资源
│   │   └── api/             # API 服务
│   ├── public/              # 静态资源
│   └── package.json         # 依赖配置
│
├── backend/                 # 后端代码
│   ├── app/                 # 应用代码
│   │   ├── api/             # API 端点
│   │   ├── auth/            # 认证相关
│   │   ├── config/          # 配置文件
│   │   ├── core/            # 核心功能
│   │   ├── crud/            # CRUD 操作
│   │   ├── middleware/      # 中间件
│   │   ├── models/          # 数据模型
│   │   ├── routers/         # API路由
│   │   ├── schemas/         # 数据验证模式
│   │   ├── services/        # 服务层
│   │   └── utils/           # 工具函数
│   ├── db_backup/           # 数据库备份目录
│   ├── main.py              # 主程序
│   ├── init_combined.py     # 统一的数据库初始化脚本
│   ├── init_db.py           # 数据库表初始化脚本
│   ├── init_users.py        # 用户初始化脚本
│   ├── diagnose_db.py       # 数据库诊断工具
│   └── requirements.txt     # 依赖配置
│
├── start.ps1                # 一键启动脚本
└── README.md                # 项目说明
```

## 项目优化

我们最近对项目进行了以下优化：

1. **改进的数据库初始化**：
   - 创建了统一的初始化脚本 `init_combined.py`，解决了表创建和用户初始化的顺序问题
   - 添加了手动SQL创建表的备选方案，确保表始终能正确创建
   - 添加详细的日志记录和错误处理

2. **编码问题解决**：
   - 解决了UTF-8编码问题，确保中文日志正确显示
   - 在PowerShell和Python之间正确传递和处理编码

3. **数据库备份与恢复**：
   - 自动备份旧的数据库文件，带有时间戳
   - 提供数据库诊断工具，可以检查和修复常见问题

4. **错误处理与交互**：
   - 增强的错误处理流程，提供详细的错误信息
   - 交互式流程，允许用户在关键步骤选择继续或停止

## 数据库问题排查

如果遇到数据库相关的问题，可以使用我们提供的诊断工具和解决方案：

### 1. 数据库表创建问题

如果遇到 "no such table: users" 等错误，可能是因为：
- SQLAlchemy ORM模型注册问题
- 表名大小写不一致
- 编码问题导致SQL执行失败

**解决方案**：
1. 运行数据库诊断工具：
   ```bash
   cd backend
   python diagnose_db.py
   ```

2. 使用统一初始化脚本重新创建数据库：
   ```bash
   cd backend
   python init_combined.py
   ```

3. 如果问题仍然存在，可以尝试手动清除数据库并重新启动：
   ```bash
   # 删除数据库文件
   rm backend/app.db
   # 重新启动服务
   .\start.ps1
   ```

### 2. 编码问题

如果看到中文乱码，可以：

1. 确保PowerShell使用UTF-8编码：
   ```powershell
   chcp 65001
   ```

2. 确保Python脚本使用UTF-8编码保存：
   ```python
   # 文件开头添加
   # -*- coding: utf-8 -*-
   ```

3. 设置环境变量：
   ```powershell
   $env:PYTHONIOENCODING = "utf-8"
   ```

### 3. 自定义排查步骤

如果仍然遇到问题，可以按照以下步骤进行详细排查：

1. **查看日志文件**：
   - 数据库初始化日志：`backend/db_init_log.txt`
   - 数据库诊断日志：`backend/db_diagnose_log.txt`

2. **检查表结构**：
   ```sql
   -- 在SQLite中执行
   .tables
   .schema users
   ```

3. **验证数据库连接**：
   ```python
   from app.database import engine
   with engine.connect() as conn:
       result = conn.execute("SELECT 1").fetchone()
       print(result)
   ```

## 许可证

MIT
