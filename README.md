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

为了简化开发环境设置，我们提供了一个增强版的启动脚本，可以自动检查和准备环境，并启动前后端服务。

```bash
# Windows
.\start_enhanced.ps1

# 如果遇到执行策略限制，可以使用以下命令暂时放行
PowerShell -ExecutionPolicy Bypass -File .\start_enhanced.ps1
```

增强版启动脚本具有以下特性：
- 详细的日志记录（保存在 logs 目录）
- 自动检查并创建虚拟环境
- 同时支持 `.venv` 和 `venv` 两种虚拟环境目录
- 自动安装前后端依赖
- 优化的服务启动方式
- 错误诊断和恢复建议

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
python init_db.py  # 注意：使用根目录的脚本，不要使用 scripts 目录中的脚本
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
│   ├── scripts/             # 脚本 (精简后)
│   ├── main.py              # 主程序
│   ├── init_db.py           # 数据库初始化
│   ├── init_users.py        # 用户初始化
│   └── requirements.txt     # 依赖配置
│
├── logs/                    # 日志目录
├── start_enhanced.ps1       # 增强版启动脚本
├── clean_duplicate_files.py # 重复文件清理脚本
└── README.md                # 项目说明
```

## 项目优化

我们最近对项目结构进行了以下优化：

1. 清理了重复功能的文件：
   - 移除了 `backend/scripts/` 目录下与根目录功能重复的脚本
   - 统一使用根目录的初始化脚本

2. 改进了启动流程：
   - 创建了更强大的 `start_enhanced.ps1` 脚本
   - 添加了详细的日志记录
   - 增加了环境检查和自动修复功能

3. 模型定义整合建议：
   - 推荐使用模块化方式组织模型
   - 将 `backend/app/models.py` 中的模型拆分到 `backend/app/models/` 目录下

## 常见问题排查

### 虚拟环境问题

如果遇到虚拟环境相关问题，可以尝试以下步骤：

1. 删除并重新创建虚拟环境
```bash
cd backend
# 删除旧的虚拟环境
Remove-Item -Recurse -Force .venv  # Windows (.venv)
# 或
# Remove-Item -Recurse -Force venv  # Windows (venv)
rm -rf .venv                       # Linux/Mac (.venv)
# 或
# rm -rf venv                       # Linux/Mac (venv)

# 创建新的虚拟环境
python -m venv .venv  # 推荐
# 或
# python -m venv venv
```

2. 确认 Python 版本兼容性
```bash
python --version  # 应为 3.8 及以上版本
```

3. 检查 pip 是否正常工作
```bash
.\.venv\Scripts\python.exe -m pip --version  # Windows (.venv)
# 或
# .\venv\Scripts\python.exe -m pip --version  # Windows (venv)
./.venv/bin/python -m pip --version         # Linux/Mac (.venv)
# 或
# ./venv/bin/python -m pip --version         # Linux/Mac (venv)
```

### 启动服务问题

如果服务无法正常启动，可以查看以下日志文件：

1. 启动脚本日志
   - 位于 `logs/startup_*.log`

2. 后端服务日志
   - 检查控制台输出

3. 前端服务日志
   - 检查控制台输出

### 编码问题

如果遇到中文显示乱码，可以：

1. 确保所有文件以 UTF-8 with BOM 编码保存
2. 在 PowerShell 中执行 `chcp 65001` 设置控制台编码为 UTF-8

## 源代码管理与 GitHub 连接

要将本项目连接到 GitHub：

1. 确保已安装并配置 Git
```bash
git --version
git config --global user.name "您的GitHub用户名"
git config --global user.email "您的GitHub邮箱"
```

2. 在 GitHub 上创建新仓库

3. 在项目根目录初始化 Git 仓库
```bash
git init
git add .
git commit -m "初始提交"
git branch -M main
git remote add origin https://github.com/您的用户名/any-go.git
git push -u origin main
```

## 许可证

MIT
