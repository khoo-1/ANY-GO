from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接配置
# 如果环境变量中有 DATABASE_URL，则使用它，否则使用 SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# 如果使用 SQLite，确保 URL 格式正确
if DATABASE_URL.startswith("sqlite"):
    # SQLite 连接参数
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL 或其他数据库的连接参数
    connect_args = {}

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, connect_args=connect_args
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库
def init_db():
    Base.metadata.create_all(bind=engine)
    print(f"数据库初始化完成，使用连接: {DATABASE_URL}")