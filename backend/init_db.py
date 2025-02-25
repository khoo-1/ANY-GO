from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, DATABASE_URL
from app.models import User, Product, PackingList, PackingListItem
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 如果使用 SQLite，确保 URL 格式正确
if DATABASE_URL.startswith("sqlite"):
    # SQLite 连接参数
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL 或其他数据库的连接参数
    connect_args = {}

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# 创建所有表
Base.metadata.create_all(bind=engine)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 添加初始用户
def create_initial_users():
    # 检查是否已存在用户
    if db.query(User).first() is None:
        # 管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=pwd_context.hash("admin123"),
            full_name="管理员",
            role="admin",
            permissions=["users:read", "users:write", "products:read", "products:write", 
                        "packing_lists:read", "packing_lists:write", "profit:read", "stock:read"],
            disabled=False
        )
        
        # 普通用户
        normal_user = User(
            username="user",
            email="user@example.com",
            hashed_password=pwd_context.hash("user123"),
            full_name="普通用户",
            role="user",
            permissions=["products:read", "packing_lists:read", "profit:read", "stock:read"],
            disabled=False
        )
        
        db.add(admin_user)
        db.add(normal_user)
        db.commit()
        print("初始用户创建成功")
    else:
        print("用户已存在，跳过创建")

# 添加示例产品
def create_sample_products():
    # 检查是否已存在产品
    if db.query(Product).first() is None:
        # 创建示例产品
        products = [
            Product(
                name="便携式蓝牙音箱",
                sku="BT-SPEAKER-001",
                description="防水便携式蓝牙音箱，电池续航20小时",
                price=29.99,
                cost=15.00,
                weight=0.5,
                stock=100,
                category="电子产品",
                supplier="音频设备供应商",
                tags=["音频", "便携", "蓝牙"]
            ),
            Product(
                name="无线充电器",
                sku="WL-CHARGER-002",
                description="10W快速无线充电器，兼容多种手机型号",
                price=15.99,
                cost=5.00,
                weight=0.2,
                stock=150,
                category="电子产品",
                supplier="手机配件供应商",
                tags=["充电器", "无线", "手机配件"]
            ),
            Product(
                name="智能手表",
                sku="SW-WATCH-003",
                description="健康监测智能手表，支持多种运动模式",
                price=49.99,
                cost=20.00,
                weight=0.1,
                stock=80,
                category="电子产品",
                supplier="智能穿戴供应商",
                tags=["智能手表", "穿戴设备", "健康监测"]
            )
        ]
        
        db.add_all(products)
        db.commit()
        print("示例产品创建成功")
    else:
        print("产品已存在，跳过创建")

# 添加示例装箱单
def create_sample_packing_list():
    # 检查是否已存在装箱单
    if db.query(PackingList).first() is None:
        # 获取管理员用户
        admin = db.query(User).filter(User.username == "admin").first()
        
        if admin:
            # 创建装箱单
            packing_list = PackingList(
                name="美国客户A装箱单",
                description="发往美国纽约的装箱单",
                status="draft",
                created_by=admin.id
            )
            
            db.add(packing_list)
            db.commit()
            
            # 获取产品
            products = db.query(Product).all()
            
            # 添加装箱单明细
            for product in products:
                item = PackingListItem(
                    packing_list_id=packing_list.id,
                    product_id=product.id,
                    quantity=5,
                    notes="测试装箱单明细"
                )
                db.add(item)
            
            db.commit()
            print("示例装箱单创建成功")
        else:
            print("找不到管理员用户，跳过创建装箱单")
    else:
        print("装箱单已存在，跳过创建")

if __name__ == "__main__":
    print(f"开始初始化数据库... 使用连接: {DATABASE_URL}")
    create_initial_users()
    create_sample_products()
    create_sample_packing_list()
    print("数据库初始化完成！")
    db.close() 