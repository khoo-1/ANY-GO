# -*- coding: utf-8 -*-
# 统一的数据库初始化脚本
# 同时处理数据库表创建和用户初始化

import os
import sys
import io
import json
import traceback
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext

# 强制启用UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
os.environ["PYTHONIOENCODING"] = "utf-8"

# 检查控制台编码
if sys.stdout.encoding != 'utf-8':
    try:
        # Windows终端使用gbk可能导致问题
        sys.stdout.reconfigure(encoding='utf-8')
        print("已重新配置控制台为UTF-8")
    except:
        print("无法重新配置控制台编码，可能会显示乱码")

# 获取正确的基目录和导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(current_dir))

# 加载环境变量
load_dotenv()

# 创建日志文件
log_file = os.path.join(current_dir, "db_init_log.txt")
with open(log_file, "w", encoding="utf-8") as f:
    f.write("=" * 50 + "\n")
    f.write(f"数据库初始化开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 50 + "\n")

def log_message(message):
    """将消息同时输出到控制台和日志文件"""
    print(message)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

# 输出编码信息
encoding_info = f"控制台编码: {sys.stdout.encoding}, 环境变量PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING')}"
log_message(encoding_info)

log_message("=" * 50)
log_message("数据库初始化开始")
log_message("=" * 50)

# 手动定义用户和产品模型，避免导入问题
DATABASE_URL = "sqlite:///./app.db"
log_message(f"使用数据库URL: {DATABASE_URL}")

# 如果使用 SQLite，确保 URL 格式正确
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # SQLite 连接参数
    connect_args = {"check_same_thread": False}
    log_message(f"使用SQLite数据库: {DATABASE_URL}")
else:
    # PostgreSQL 或其他数据库的连接参数
    log_message(f"使用非SQLite数据库: {DATABASE_URL}")

# 提取SQLite数据库文件路径
db_path = DATABASE_URL.replace("sqlite:///", "")
if db_path.startswith("./"):
    db_path = db_path[2:]  # 移除开头的 ./
db_path = os.path.join(current_dir, db_path)
log_message(f"数据库文件路径: {db_path}")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

# 创建模型基类
metadata = MetaData()
Base = declarative_base(metadata=metadata)

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

# 检查模型注册
tables_in_metadata = list(metadata.tables.keys())
log_message(f"Base.metadata中注册的表: {tables_in_metadata}")

# 测试中文输出
log_message("测试中文输出: 用户、产品、装箱单")

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def check_table_exists(engine, table_name):
    """检查表是否存在，不区分大小写"""
    try:
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        log_message(f"数据库中的所有表: {all_tables}")
        
        # 不区分大小写检查
        return any(table.lower() == table_name.lower() for table in all_tables)
    except Exception as e:
        log_message(f"检查表时出错: {e}")
        return False

def print_table_details(engine, model_class):
    """打印模型类和对应数据库表的详细信息"""
    try:
        table_name = model_class.__tablename__
        log_message(f"模型类 {model_class.__name__} 对应的表名: {table_name}")
        
        inspector = inspect(engine)
        if check_table_exists(engine, table_name):
            columns = inspector.get_columns(table_name)
            log_message(f"表 {table_name} 的列信息:")
            for column in columns:
                log_message(f"  - {column['name']}: {column['type']}")
        else:
            log_message(f"警告: 表 {table_name} 在数据库中不存在!")
    except Exception as e:
        log_message(f"打印表详细信息时出错: {e}")

def create_tables_with_sqlite():
    """使用原生SQLite直接创建表"""
    log_message("使用原生SQLite直接创建表...")
    
    try:
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # 连接SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
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
        ''')
        log_message("用户表创建完成")
        
        # 创建产品表
        cursor.execute('''
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
        ''')
        log_message("产品表创建完成")
        
        # 创建装箱单表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS packing_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            status VARCHAR(20) NOT NULL,
            created_by INTEGER NOT NULL,
            created_at VARCHAR(50),
            updated_at VARCHAR(50)
        )
        ''')
        log_message("装箱单表创建完成")
        
        # 创建装箱单明细表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS packing_list_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            packing_list_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            notes TEXT,
            created_at VARCHAR(50),
            updated_at VARCHAR(50)
        )
        ''')
        log_message("装箱单明细表创建完成")
        
        # 提交事务
        conn.commit()
        log_message("所有表创建成功")
        
        # 列出所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        log_message(f"SQLite数据库中的表: {[t[0] for t in tables]}")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        log_message(f"使用SQLite创建表时出错: {e}")
        traceback.print_exc()
        return False

def init_database():
    """初始化数据库，创建表并添加初始数据"""
    log_message(f"开始初始化数据库... 使用连接: {DATABASE_URL}")
    
    # 检查数据库表
    try:
        # 尝试两种方法创建表
        sqlalchemy_success = False
        sqlite_success = False
        
        # 1. 先尝试使用SQLAlchemy ORM创建表
        try:
            log_message("使用SQLAlchemy ORM创建表...")
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            log_message(f"初始化前数据库中已存在的表: {existing_tables}")
            
            # 创建所有表
            Base.metadata.create_all(bind=engine)
            log_message("SQLAlchemy表创建完成")
            
            # 验证表创建
            inspector = inspect(engine)
            updated_tables = inspector.get_table_names()
            log_message(f"创建后的表: {updated_tables}")
            
            # 检查必要的表
            required_tables = ['users', 'products', 'packing_lists', 'packing_list_items']
            missing_tables = [t for t in required_tables if t not in updated_tables]
            
            if not missing_tables:
                log_message("SQLAlchemy成功创建了所有必要的表")
                sqlalchemy_success = True
            else:
                log_message(f"SQLAlchemy未能创建以下表: {missing_tables}")
        except Exception as e:
            log_message(f"SQLAlchemy创建表时出错: {e}")
            traceback.print_exc()
        
        # 2. 如果SQLAlchemy失败，使用原生SQLite创建表
        if not sqlalchemy_success:
            log_message("SQLAlchemy创建表失败，尝试使用原生SQLite...")
            sqlite_success = create_tables_with_sqlite()
            
            if sqlite_success:
                log_message("原生SQLite成功创建了所有表")
            else:
                log_message("原生SQLite创建表失败")
        
        # 如果两种方法都失败，抛出异常
        if not (sqlalchemy_success or sqlite_success):
            raise Exception("使用SQLAlchemy和原生SQLite都无法创建表")
        
        # 打印模型和表的详细信息
        log_message("\n======= 模型和表的详细信息 =======")
        print_table_details(engine, User)
        print_table_details(engine, Product)
        print_table_details(engine, PackingList)
        print_table_details(engine, PackingListItem)
        log_message("===================================\n")
        
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
            log_message("所有数据初始化完成!")
            
        except Exception as e:
            db.rollback()
            log_message(f"初始化数据时出错: {e}")
            traceback.print_exc()
            raise
        finally:
            db.close()
    
    except Exception as e:
        log_message(f"创建表时出错: {e}")
        traceback.print_exc()
        raise

def init_users(db, engine):
    """初始化用户数据"""
    log_message("开始初始化用户...")
    
    try:
        # 验证用户表存在
        if not check_table_exists(engine, "users"):
            log_message("用户表不存在，尝试使用SQLite直接创建...")
            # 尝试再次创建表
            create_tables_with_sqlite()
            
            # 再次检查表是否存在
            if not check_table_exists(engine, "users"):
                raise Exception("用户表不存在，无法初始化用户!")
        
        # 检查是否已存在用户
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            log_message(f"现有用户数量: {result}")
            
            if result == 0:
                log_message("没有现有用户，开始创建...")
                
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
                    :username, :email, :hashed_password, :fullname, :role, 
                    :permissions, :disabled, :created, :updated
                )
                """), {
                    "username": "admin",
                    "email": "admin@example.com",
                    "hashed_password": admin_password,
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
                    :username, :email, :hashed_password, :fullname, :role, 
                    :permissions, :disabled, :created, :updated
                )
                """), {
                    "username": "user",
                    "email": "user@example.com",
                    "hashed_password": user_password,
                    "fullname": "普通用户",
                    "role": "user",
                    "permissions": user_permissions,
                    "disabled": 0,
                    "created": datetime.now().isoformat(),
                    "updated": datetime.now().isoformat()
                })
                
                # 提交事务
                conn.commit()
                log_message("用户初始化完成")
                
                # 验证用户创建
                count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                log_message(f"创建后的用户数量: {count}")
                
                # 列出所有用户
                users = conn.execute(text("SELECT id, username FROM users")).fetchall()
                log_message(f"用户列表: {users}")
            else:
                log_message(f"已存在 {result} 个用户，跳过创建")
    except Exception as e:
        log_message(f"初始化用户时出错: {e}")
        traceback.print_exc()
        raise

def init_products(db, engine):
    """初始化产品数据"""
    log_message("开始初始化产品...")
    
    try:
        # 检查是否已存在产品
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            if result == 0:
                log_message("没有现有产品，开始创建...")
                
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
                log_message(f"已创建 {len(products)} 个示例产品")
            else:
                log_message(f"已存在 {result} 个产品，跳过创建")
    except Exception as e:
        log_message(f"初始化产品时出错: {e}")
        traceback.print_exc()
        raise

def init_packing_lists(db, engine):
    """初始化装箱单数据"""
    log_message("开始初始化装箱单...")
    
    try:
        # 检查是否已存在装箱单
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM packing_lists")).scalar()
            if result == 0:
                log_message("没有现有装箱单，开始创建...")
                
                # 获取管理员用户ID
                admin_id = conn.execute(text("SELECT id FROM users WHERE username = 'admin'")).scalar()
                if admin_id:
                    log_message(f"找到管理员用户ID: {admin_id}")
                    
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
                    log_message(f"创建了装箱单ID: {packing_list_id}")
                    
                    # 获取所有产品ID
                    product_ids = [row[0] for row in conn.execute(text("SELECT id FROM products")).fetchall()]
                    log_message(f"找到 {len(product_ids)} 个产品添加到装箱单")
                    
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
                    log_message("装箱单和明细初始化完成")
                else:
                    log_message("找不到管理员用户，跳过创建装箱单")
            else:
                log_message(f"已存在 {result} 个装箱单，跳过创建")
    except Exception as e:
        log_message(f"初始化装箱单时出错: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    try:
        # 尝试安全地删除旧数据库文件
        if os.path.exists(db_path):
            log_message(f"尝试删除旧数据库文件: {db_path}")
            try:
                # 尝试直接删除
                os.remove(db_path)
                log_message("旧数据库文件删除成功")
            except PermissionError:
                log_message("无法直接删除数据库文件，可能被其他进程锁定")
                
                # 尝试终止可能的Python进程
                log_message("尝试终止可能锁定数据库的进程...")
                
                # 仅在Windows上执行
                if os.name == 'nt':
                    try:
                        # 尝试使用强制方式
                        import psutil
                        for proc in psutil.process_iter():
                            try:
                                if proc.name().lower() == 'python.exe':
                                    log_message(f"终止Python进程: {proc.pid}")
                                    proc.kill()
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                pass
                    except ImportError:
                        log_message("未安装psutil模块，无法自动终止进程")
                
                # 等待一段时间
                import time
                time.sleep(1)
                
                # 再次尝试删除
                try:
                    os.remove(db_path)
                    log_message("第二次尝试删除成功")
                except:
                    log_message("仍然无法删除数据库文件，请手动删除")
                    input("按任意键继续...")
        
        # 初始化数据库
        init_database()
        
        # 验证数据库
        if os.path.exists(db_path):
            size_kb = os.path.getsize(db_path) / 1024
            log_message(f"数据库文件已创建: {db_path} (大小: {size_kb:.2f} KB)")
            
            # 验证表存在
            inspector = inspect(engine)
            final_tables = inspector.get_table_names()
            log_message(f"最终数据库中的表: {final_tables}")
            
            required_tables = ['users', 'products', 'packing_lists', 'packing_list_items']
            missing_tables = [t for t in required_tables if t not in final_tables]
            
            if not missing_tables:
                log_message("所有必要的表已成功创建 ✓")
            else:
                log_message(f"警告: 以下表仍然缺失: {missing_tables}")
        else:
            log_message(f"错误: 数据库文件未创建!")
        
        log_message("=" * 50)
        log_message("数据库初始化成功！")
        log_message("=" * 50)
        
        # 将日志写入文件
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write(f"数据库初始化成功 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n")
        
    except Exception as e:
        log_message("=" * 50)
        log_message(f"数据库初始化失败: {e}")
        traceback.print_exc()
        log_message("=" * 50)
        
        # 记录错误到日志
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write(f"数据库初始化失败 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"错误: {str(e)}\n")
            f.write("=" * 50 + "\n")
            
            # 添加traceback到日志
            f.write(traceback.format_exc() + "\n")
        
        sys.exit(1) 