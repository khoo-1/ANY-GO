# 统一的数据库初始化脚本
# 同时处理数据库表创建和用户初始化

import os
import sys
import json
import traceback
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext

# 强制启用UTF-8编码
if sys.stdout.encoding != 'utf-8':
    try:
        # Windows终端使用gbk可能导致问题
        sys.stdout.reconfigure(encoding='utf-8')
        print("已重新配置控制台为UTF-8")
    except:
        print("无法重新配置控制台编码，可能会显示乱码")

# 设置输出编码
os.environ["PYTHONIOENCODING"] = "utf-8"

# 获取正确的基目录和导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(current_dir))

# 加载环境变量
load_dotenv()

print("=" * 50)
print("数据库初始化开始")
print("=" * 50)

# 创建日志文件
log_file = os.path.join(current_dir, "db_init_log.txt")
with open(log_file, "w", encoding="utf-8") as f:
    f.write("=" * 50 + "\n")
    f.write(f"数据库初始化开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 50 + "\n")

# 手动定义用户和产品模型，避免导入问题
DATABASE_URL = "sqlite:///./app.db"
print(f"使用数据库URL: {DATABASE_URL}")

# 如果使用 SQLite，确保 URL 格式正确
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # SQLite 连接参数
    connect_args = {"check_same_thread": False}
    print(f"使用SQLite数据库: {DATABASE_URL}")
else:
    # PostgreSQL 或其他数据库的连接参数
    print(f"使用非SQLite数据库: {DATABASE_URL}")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=True)

# 创建模型基类
Base = declarative_base()

# 创建表结构模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), nullable=False)
    permissions = Column(String(500))  # 存储JSON字符串
    disabled = Column(Integer, default=0)
    created_at = Column(String(50), default=datetime.now().isoformat())
    updated_at = Column(String(50), default=datetime.now().isoformat())

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    description = Column(String(500))
    price = Column(Integer, nullable=False)  # 存储为整数，显示时除以100
    cost = Column(Integer, nullable=False)  # 存储为整数，显示时除以100
    weight = Column(Integer)
    stock = Column(Integer, nullable=False, default=0)
    category = Column(String(50))
    supplier = Column(String(100))
    tags = Column(String(500))  # 存储JSON字符串
    created_at = Column(String(50), default=datetime.now().isoformat())
    updated_at = Column(String(50), default=datetime.now().isoformat())

class PackingList(Base):
    __tablename__ = "packing_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    status = Column(String(20), nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(String(50), default=datetime.now().isoformat())
    updated_at = Column(String(50), default=datetime.now().isoformat())

class PackingListItem(Base):
    __tablename__ = "packing_list_items"
    
    id = Column(Integer, primary_key=True, index=True)
    packing_list_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    notes = Column(String(500))
    created_at = Column(String(50), default=datetime.now().isoformat())
    updated_at = Column(String(50), default=datetime.now().isoformat())

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def check_table_exists(engine, table_name):
    """检查表是否存在，不区分大小写"""
    try:
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        print(f"数据库中的所有表: {all_tables}")
        
        # 不区分大小写检查
        return any(table.lower() == table_name.lower() for table in all_tables)
    except Exception as e:
        print(f"检查表时出错: {e}")
        return False

def print_table_details(engine, model_class):
    """打印模型类和对应数据库表的详细信息"""
    try:
        table_name = model_class.__tablename__
        print(f"模型类 {model_class.__name__} 对应的表名: {table_name}")
        
        inspector = inspect(engine)
        if check_table_exists(engine, table_name):
            columns = inspector.get_columns(table_name)
            print(f"表 {table_name} 的列信息:")
            for column in columns:
                print(f"  - {column['name']}: {column['type']}")
        else:
            print(f"警告: 表 {table_name} 在数据库中不存在!")
    except Exception as e:
        print(f"打印表详细信息时出错: {e}")

def init_database():
    """初始化数据库，创建表并添加初始数据"""
    print(f"开始初始化数据库... 使用连接: {DATABASE_URL}")
    
    # 检查数据库表
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"初始化前数据库中已存在的表: {existing_tables}")
        
        # 创建所有表
        print("开始创建所有表...")
        Base.metadata.create_all(bind=engine)
        print("表创建完成")
        
        # 验证表创建
        inspector = inspect(engine)
        updated_tables = inspector.get_table_names()
        print(f"创建后的表: {updated_tables}")
        
        # 检查必要的表是否创建
        required_tables = ['users', 'products', 'packing_lists', 'packing_list_items']
        missing_tables = [t for t in required_tables if t not in updated_tables]
        
        if missing_tables:
            print(f"警告: 以下表未创建: {missing_tables}")
            print("尝试使用SQLite直接创建...")
            
            # 打开SQLite连接
            with engine.connect() as conn:
                # 创建用户表
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    hashed_password VARCHAR(100) NOT NULL,
                    full_name VARCHAR(100),
                    role VARCHAR(20) NOT NULL,
                    permissions TEXT,
                    disabled INTEGER DEFAULT 0,
                    created_at VARCHAR(50),
                    updated_at VARCHAR(50)
                )
                """))
                print("用户表创建完成")
                
                # 创建产品表
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    sku VARCHAR(50) UNIQUE NOT NULL,
                    description TEXT,
                    price INTEGER NOT NULL,
                    cost INTEGER NOT NULL,
                    weight INTEGER,
                    stock INTEGER NOT NULL DEFAULT 0,
                    category VARCHAR(50),
                    supplier VARCHAR(100),
                    tags TEXT,
                    created_at VARCHAR(50),
                    updated_at VARCHAR(50)
                )
                """))
                print("产品表创建完成")
                
                # 创建装箱单表
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS packing_lists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    status VARCHAR(20) NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at VARCHAR(50),
                    updated_at VARCHAR(50)
                )
                """))
                print("装箱单表创建完成")
                
                # 创建装箱单明细表
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS packing_list_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    packing_list_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    notes TEXT,
                    created_at VARCHAR(50),
                    updated_at VARCHAR(50)
                )
                """))
                print("装箱单明细表创建完成")
                
                # 提交事务
                conn.commit()
            
            # 再次验证表创建
            inspector = inspect(engine)
            final_tables = inspector.get_table_names()
            print(f"直接创建后的表: {final_tables}")
        
        # 打印模型和表的详细信息
        print("\n======= 模型和表的详细信息 =======")
        print_table_details(engine, User)
        print_table_details(engine, Product)
        print_table_details(engine, PackingList)
        print_table_details(engine, PackingListItem)
        print("===================================\n")
        
        # 创建会话
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 初始化用户
            init_users(db, engine)
            
            # 初始化产品
            init_products(db, engine)
            
            # 初始化装箱单
            init_packing_lists(db, engine)
            
            # 提交所有更改
            db.commit()
            print("所有数据初始化完成!")
            
        except Exception as e:
            db.rollback()
            print(f"初始化数据时出错: {e}")
            traceback.print_exc()
            raise
        finally:
            db.close()
    
    except Exception as e:
        print(f"创建表时出错: {e}")
        traceback.print_exc()
        raise

def init_users(db, engine):
    """初始化用户数据"""
    print("开始初始化用户...")
    
    try:
        # 验证用户表存在
        if not check_table_exists(engine, "users"):
            raise Exception("用户表不存在，无法初始化用户!")
        
        # 检查是否已存在用户
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            if result == 0:
                print("没有现有用户，开始创建...")
                
                # 添加管理员用户
                admin_password = get_password_hash("admin123")
                admin_permissions = json.dumps([
                    "users:read", "users:write", 
                    "products:read", "products:write", 
                    "packing_lists:read", "packing_lists:write", 
                    "profit:read", "stock:read"
                ])
                
                conn.execute(text("""
                INSERT INTO users (
                    username, email, hashed_password, full_name, role, 
                    permissions, disabled, created_at, updated_at
                ) VALUES (
                    :username, :email, :password, :fullname, :role, 
                    :permissions, :disabled, :created, :updated
                )
                """), {
                    "username": "admin",
                    "email": "admin@example.com",
                    "password": admin_password,
                    "fullname": "管理员",
                    "role": "admin",
                    "permissions": admin_permissions,
                    "disabled": 0,
                    "created": datetime.now().isoformat(),
                    "updated": datetime.now().isoformat()
                })
                
                # 添加普通用户
                user_password = get_password_hash("user123")
                user_permissions = json.dumps([
                    "products:read", "packing_lists:read", 
                    "profit:read", "stock:read"
                ])
                
                conn.execute(text("""
                INSERT INTO users (
                    username, email, hashed_password, full_name, role, 
                    permissions, disabled, created_at, updated_at
                ) VALUES (
                    :username, :email, :password, :fullname, :role, 
                    :permissions, :disabled, :created, :updated
                )
                """), {
                    "username": "user",
                    "email": "user@example.com",
                    "password": user_password,
                    "fullname": "普通用户",
                    "role": "user",
                    "permissions": user_permissions,
                    "disabled": 0,
                    "created": datetime.now().isoformat(),
                    "updated": datetime.now().isoformat()
                })
                
                # 提交事务
                conn.commit()
                print("用户初始化完成")
            else:
                print(f"已存在 {result} 个用户，跳过创建")
    except Exception as e:
        print(f"初始化用户时出错: {e}")
        traceback.print_exc()
        raise

def init_products(db, engine):
    """初始化产品数据"""
    print("开始初始化产品...")
    
    try:
        # 检查是否已存在产品
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            if result == 0:
                print("没有现有产品，开始创建...")
                
                # 产品数据
                products = [
                    {
                        "name": "便携式蓝牙音箱",
                        "sku": "BT-SPEAKER-001",
                        "description": "防水便携式蓝牙音箱，电池续航20小时",
                        "price": 2999,  # 29.99
                        "cost": 1500,   # 15.00
                        "weight": 500,  # 0.5kg
                        "stock": 100,
                        "category": "电子产品",
                        "supplier": "音频设备供应商",
                        "tags": json.dumps(["音频", "便携", "蓝牙"])
                    },
                    {
                        "name": "无线充电器",
                        "sku": "WL-CHARGER-002",
                        "description": "10W快速无线充电器，兼容多种手机型号",
                        "price": 1599,  # 15.99
                        "cost": 500,    # 5.00
                        "weight": 200,  # 0.2kg
                        "stock": 150,
                        "category": "电子产品",
                        "supplier": "手机配件供应商",
                        "tags": json.dumps(["充电器", "无线", "手机配件"])
                    },
                    {
                        "name": "智能手表",
                        "sku": "SW-WATCH-003",
                        "description": "健康监测智能手表，支持多种运动模式",
                        "price": 4999,  # 49.99
                        "cost": 2000,   # 20.00
                        "weight": 100,  # 0.1kg
                        "stock": 80,
                        "category": "电子产品",
                        "supplier": "智能穿戴供应商",
                        "tags": json.dumps(["智能手表", "穿戴设备", "健康监测"])
                    }
                ]
                
                # 插入产品
                for product in products:
                    conn.execute(text("""
                    INSERT INTO products (
                        name, sku, description, price, cost, weight, stock, 
                        category, supplier, tags, created_at, updated_at
                    ) VALUES (
                        :name, :sku, :description, :price, :cost, :weight, :stock, 
                        :category, :supplier, :tags, :created, :updated
                    )
                    """), {
                        **product,
                        "created": datetime.now().isoformat(),
                        "updated": datetime.now().isoformat()
                    })
                
                # 提交事务
                conn.commit()
                print(f"已创建 {len(products)} 个示例产品")
            else:
                print(f"已存在 {result} 个产品，跳过创建")
    except Exception as e:
        print(f"初始化产品时出错: {e}")
        traceback.print_exc()
        raise

def init_packing_lists(db, engine):
    """初始化装箱单数据"""
    print("开始初始化装箱单...")
    
    try:
        # 检查是否已存在装箱单
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM packing_lists")).scalar()
            if result == 0:
                print("没有现有装箱单，开始创建...")
                
                # 获取管理员用户ID
                admin_id = conn.execute(text("SELECT id FROM users WHERE username = 'admin'")).scalar()
                if admin_id:
                    print(f"找到管理员用户ID: {admin_id}")
                    
                    # 创建装箱单
                    conn.execute(text("""
                    INSERT INTO packing_lists (
                        name, description, status, created_by, created_at, updated_at
                    ) VALUES (
                        :name, :description, :status, :created_by, :created, :updated
                    )
                    """), {
                        "name": "美国客户A装箱单",
                        "description": "发往美国纽约的装箱单",
                        "status": "draft",
                        "created_by": admin_id,
                        "created": datetime.now().isoformat(),
                        "updated": datetime.now().isoformat()
                    })
                    
                    # 获取新创建的装箱单ID
                    packing_list_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()
                    print(f"创建了装箱单ID: {packing_list_id}")
                    
                    # 获取所有产品ID
                    product_ids = [row[0] for row in conn.execute(text("SELECT id FROM products")).fetchall()]
                    print(f"找到 {len(product_ids)} 个产品添加到装箱单")
                    
                    # 添加装箱单明细
                    for idx, product_id in enumerate(product_ids):
                        conn.execute(text("""
                        INSERT INTO packing_list_items (
                            packing_list_id, product_id, quantity, notes, created_at, updated_at
                        ) VALUES (
                            :packing_list_id, :product_id, :quantity, :notes, :created, :updated
                        )
                        """), {
                            "packing_list_id": packing_list_id,
                            "product_id": product_id,
                            "quantity": 5,
                            "notes": f"测试装箱单明细 {idx+1}",
                            "created": datetime.now().isoformat(),
                            "updated": datetime.now().isoformat()
                        })
                    
                    # 提交事务
                    conn.commit()
                    print("装箱单和明细初始化完成")
                else:
                    print("找不到管理员用户，跳过创建装箱单")
            else:
                print(f"已存在 {result} 个装箱单，跳过创建")
    except Exception as e:
        print(f"初始化装箱单时出错: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    try:
        print("=" * 50)
        print("数据库初始化开始")
        print("=" * 50)
        
        # 删除旧数据库文件（如果存在）
        db_file = os.path.join(current_dir, "app.db")
        if os.path.exists(db_file):
            print(f"删除旧数据库文件: {db_file}")
            os.remove(db_file)
        
        # 初始化数据库
        init_database()
        
        print("=" * 50)
        print("数据库初始化成功！")
        print("=" * 50)
        
        # 将日志写入文件
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write(f"数据库初始化成功 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n")
        
    except Exception as e:
        print("=" * 50)
        print(f"数据库初始化失败: {e}")
        traceback.print_exc()
        print("=" * 50)
        
        # 记录错误到日志
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write(f"数据库初始化失败 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"错误: {str(e)}\n")
            f.write("=" * 50 + "\n")
            
            # 添加traceback到日志
            import traceback
            traceback_str = traceback.format_exc()
            f.write(traceback_str + "\n")
        
        sys.exit(1) 