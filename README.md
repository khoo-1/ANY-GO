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
- SQLite 数据库 (本地开发)
- PostgreSQL 数据库 (生产环境)
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
- 自动编码设置，确保中文正常显示

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
DATABASE_URL=sqlite:///./app.db
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
   - 使用直接定义模型的方式，避免动态导入可能带来的问题
   - 添加了手动SQL创建表的备选方案，确保表始终能正确创建
   - 添加详细的日志记录和错误处理

2. **数据库诊断工具**：
   - 新增 `diagnose_db.py` 诊断工具，可以检测SQLAlchemy模型注册、表创建和数据库连接问题
   - 诊断工具可以提供详细的问题分析和解决方案
   - 启动脚本集成了诊断工具，在遇到问题时自动提供诊断选项

3. **编码问题解决**：
   - 解决了Windows系统下的UTF-8编码问题，确保中文日志正确显示
   - 在PowerShell和Python之间正确传递和处理编码
   - 设置`PYTHONIOENCODING`环境变量，确保Python输出的中文正确显示

4. **数据库备份与恢复**：
   - 自动备份旧的数据库文件，带有时间戳
   - 每次启动前验证数据库完整性，发现问题时提供修复选项
   - 支持手动或自动重新初始化数据库

5. **错误处理与交互**：
   - 增强的错误处理流程，提供详细的错误信息
   - 交互式流程，允许用户在关键步骤选择继续或停止
   - 错误日志记录到文件，方便后续分析

## 数据库问题排查

如果遇到数据库相关的问题，可以使用我们提供的诊断工具和解决方案：

### 1. 数据库表创建问题

如果遇到 "no such table: users" 等错误，可能是因为：
- SQLAlchemy ORM模型注册问题（最常见原因）
- 表名大小写不一致
- 编码问题导致SQL执行失败
- 数据库文件权限问题

**解决方案**：
1. 运行数据库诊断工具：
   ```bash
   cd backend
   python diagnose_db.py
   ```
   诊断工具会自动检测并提供解决方案。

2. 使用统一初始化脚本重新创建数据库：
   ```bash
   cd backend
   # 先删除旧数据库（如果存在）
   rm app.db
   # 使用改进的初始化脚本
   python init_combined.py
   ```

3. 通过启动脚本重新初始化：
   ```bash
   # 启动脚本会备份旧数据库并尝试初始化
   .\start.ps1
   ```

### 2. 编码问题

如果看到中文乱码，可以：

1. 确保PowerShell使用UTF-8编码：
   ```powershell
   chcp 65001
   ```

2. 设置环境变量：
   ```powershell
   $env:PYTHONIOENCODING = "utf-8"
   ```

3. 确保所有Python文件使用UTF-8编码保存。

### 3. 常见问题快速解决方案

| 问题 | 解决方案 |
|------|----------|
| 提示"no such table: users" | 运行 `python init_combined.py` 重新初始化数据库 |
| 中文显示乱码 | 运行 `chcp 65001` 设置控制台编码为UTF-8 |
| 数据库文件损坏 | 删除 `app.db` 后运行 `python init_combined.py` |
| 启动脚本报错 | 使用 `PowerShell -ExecutionPolicy Bypass -File .\start.ps1` |
| 诊断工具显示"模型未注册" | 使用新的统一初始化脚本，它避免了模型导入问题 |

## 高级维护操作

对于开发者和管理员，我们提供以下高级维护操作：

1. **手动备份数据库**：
   ```bash
   cd backend
   # 将数据库备份到指定位置
   cp app.db db_backup/app.db.backup.$(date +%Y%m%d)
   ```

2. **运行完整诊断**：
   ```bash
   cd backend
   # 运行诊断并保存详细日志
   python diagnose_db.py > diagnostic_report.txt
   ```

3. **完全重置系统**（谨慎使用）：
   ```bash
   cd backend
   # 删除数据库文件
   rm app.db
   # 重新初始化
   python init_combined.py
   ```

## 更新日志

### v1.1.0 (2023-02-27)
- 添加了统一的数据库初始化脚本
- 新增数据库诊断工具
- 优化了编码处理，解决中文显示问题
- 改进了启动脚本的错误处理和用户交互

### v1.0.0 (2023-01-15)
- 初始版本发布
- 基本用户认证和权限管理
- 产品和装箱单基础功能

## 许可证

MIT
