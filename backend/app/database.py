from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# 创建数据库引擎
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=True  # 启用SQL语句日志
    )
else:
    engine = create_engine(DATABASE_URL)

# 创建会话工厂
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
    try:
        Base.metadata.create_all(bind=engine)
        print(f"数据库初始化完成，使用连接: {DATABASE_URL}")
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        if not DATABASE_URL.startswith("sqlite"):
            print("尝试使用SQLite作为备用数据库...")
            sqlite_url = "sqlite:///./app.db"
            sqlite_engine = create_engine(
                sqlite_url,
                connect_args={"check_same_thread": False}
            )
            Base.metadata.create_all(bind=sqlite_engine)
            print("使用SQLite初始化数据库成功")

# 创建所有表
def create_tables():
    # 导入所有模型
    from .models.user import User
    from .models.product import Product
    from .models.packing import PackingList, PackingItem, BoxSpecs
    
    print("开始创建数据库表...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功")