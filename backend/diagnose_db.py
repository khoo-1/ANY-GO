# 数据库诊断脚本
# 用于检查模型注册和表创建问题

import os
import sys
import json
import traceback
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, MetaData, Table, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker, declarative_base

# 强制启用UTF-8编码
try:
    # Windows终端使用gbk可能导致问题
    sys.stdout.reconfigure(encoding='utf-8')
    print("已重新配置控制台为UTF-8")
except:
    print("无法重新配置控制台编码，可能会显示乱码")

# 设置输出编码环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"

# 获取正确的基目录和导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(current_dir))

# 创建日志文件
log_file = os.path.join(current_dir, "db_diagnose_log.txt")
with open(log_file, "w", encoding="utf-8") as f:
    f.write("=" * 50 + "\n")
    f.write(f"数据库诊断开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 50 + "\n")

def log_message(message):
    """将消息同时输出到控制台和日志文件"""
    print(message)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

log_message("=" * 50)
log_message("1. 检查系统编码环境")
log_message("=" * 50)

log_message(f"Python版本: {sys.version}")
log_message(f"系统默认编码: {sys.getdefaultencoding()}")
log_message(f"标准输出编码: {sys.stdout.encoding}")
log_message(f"文件系统编码: {sys.getfilesystemencoding()}")
log_message(f"区域设置: {os.environ.get('LANG', '未设置')}")
log_message(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', '未设置')}")

# 测试Unicode字符输出
try:
    log_message("Unicode测试: ✓ ✗ 你好 こんにちは")
    log_message("编码测试通过 ✓")
except Exception as e:
    log_message(f"编码测试失败: {e}")

log_message("\n" + "=" * 50)
log_message("2. 测试SQLite连接")
log_message("=" * 50)

# 尝试连接SQLite
DATABASE_URL = "sqlite:///./test_diagnose.db"
log_message(f"使用测试数据库URL: {DATABASE_URL}")

try:
    # 创建临时数据库引擎
    engine = create_engine(DATABASE_URL, echo=False)
    
    # 测试连接
    with engine.connect() as conn:
        result = conn.execute(text("SELECT sqlite_version()")).scalar()
        log_message(f"SQLite版本: {result}")
        log_message("数据库连接成功 ✓")
except Exception as e:
    log_message(f"数据库连接失败: {e}")
    traceback.print_exc()

# 尝试导入应用的数据库配置
log_message("\n" + "=" * 50)
log_message("3. 尝试导入应用数据库配置")
log_message("=" * 50)

app_database_url = None
app_base = None

try:
    # 先尝试直接导入
    log_message("尝试直接导入app.database...")
    try:
        from app.database import Base, DATABASE_URL
        app_base = Base
        app_database_url = DATABASE_URL
        log_message(f"成功导入app.database: {DATABASE_URL}")
    except ImportError:
        log_message("直接导入失败，尝试动态导入...")
        import importlib
        try:
            db_module = importlib.import_module("app.database")
            app_base = getattr(db_module, "Base", None)
            app_database_url = getattr(db_module, "DATABASE_URL", None)
            log_message(f"动态导入成功: {app_database_url}")
        except Exception as e:
            log_message(f"动态导入失败: {e}")
            
    # 检查导入结果
    if app_database_url:
        log_message(f"应用DATABASE_URL: {app_database_url}")
    else:
        log_message("警告: 未找到应用DATABASE_URL，将使用默认值")
        app_database_url = "sqlite:///./app.db"
    
    if app_base:
        log_message("应用Base类已导入 ✓")
        log_message(f"Base类型: {type(app_base)}")
        log_message(f"Base元数据: {getattr(app_base, 'metadata', None)}")
    else:
        log_message("警告: 未找到应用Base类，将创建新的Base")
        app_base = declarative_base()
except Exception as e:
    log_message(f"导入过程中出错: {e}")
    traceback.print_exc()
    # 创建一个新的Base
    app_base = declarative_base()
    app_database_url = "sqlite:///./app.db"

# 尝试导入模型
log_message("\n" + "=" * 50)
log_message("4. 尝试导入应用模型")
log_message("=" * 50)

models = {}
model_tables = []

try:
    # 导入模型
    log_message("尝试导入模型...")
    try:
        from app.models import User, Product, PackingList, PackingListItem
        models = {
            'User': User,
            'Product': Product,
            'PackingList': PackingList,
            'PackingListItem': PackingListItem
        }
        log_message("成功直接导入模型 ✓")
    except ImportError:
        log_message("直接导入失败，尝试动态导入...")
        import importlib
        try:
            models_module = importlib.import_module("app.models")
            for name in dir(models_module):
                obj = getattr(models_module, name)
                if hasattr(obj, '__tablename__'):
                    models[name] = obj
                    log_message(f"找到模型: {name} -> 表名: {obj.__tablename__}")
        except Exception as e:
            log_message(f"动态导入模型失败: {e}")
    
    # 检查模型
    if models:
        log_message(f"找到 {len(models)} 个模型")
        for name, model in models.items():
            if hasattr(model, '__tablename__'):
                table_name = model.__tablename__
                model_tables.append(table_name)
                log_message(f"模型 {name} -> 表 {table_name}")
            else:
                log_message(f"警告: 模型 {name} 没有 __tablename__ 属性")
    else:
        log_message("警告: 未找到任何模型")
except Exception as e:
    log_message(f"导入模型过程中出错: {e}")
    traceback.print_exc()

# 检查模型是否正确注册
log_message("\n" + "=" * 50)
log_message("5. 检查模型注册状态")
log_message("=" * 50)

if app_base:
    tables_in_metadata = list(getattr(app_base.metadata, 'tables', {}).keys())
    log_message(f"Base.metadata中注册的表: {tables_in_metadata}")
    
    # 比较模型表与元数据表
    if model_tables:
        missing_tables = [t for t in model_tables if t not in tables_in_metadata]
        if missing_tables:
            log_message(f"警告: 以下表未在Base.metadata中注册: {missing_tables}")
            log_message("可能原因:")
            log_message("1. 模型类没有继承自正确的Base类")
            log_message("2. 模型在导入时出现了循环导入问题")
            log_message("3. 模型定义后Base.metadata没有更新")
        else:
            log_message("所有模型已正确注册到Base.metadata ✓")
else:
    log_message("无法检查模型注册状态: Base对象不可用")

# 测试表创建
log_message("\n" + "=" * 50)
log_message("6. 测试表创建功能")
log_message("=" * 50)

# 创建一个测试模型
TestBase = declarative_base()

class TestModel(TestBase):
    __tablename__ = "test_diagnose_table"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

log_message(f"创建测试模型: {TestModel.__tablename__}")

# 尝试创建测试表
try:
    # 使用内存数据库
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    TestBase.metadata.create_all(test_engine)
    
    # 验证测试表创建
    inspector = inspect(test_engine)
    test_tables = inspector.get_table_names()
    log_message(f"测试表创建结果: {test_tables}")
    
    if "test_diagnose_table" in test_tables:
        log_message("测试表创建成功 ✓")
    else:
        log_message("测试表创建失败 ✗")
        
except Exception as e:
    log_message(f"测试表创建出错: {e}")
    traceback.print_exc()

# 检查实际应用数据库
log_message("\n" + "=" * 50)
log_message("7. 检查应用数据库")
log_message("=" * 50)

try:
    app_engine = create_engine(app_database_url, echo=False)
    
    # 连接测试
    log_message(f"连接到应用数据库: {app_database_url}")
    with app_engine.connect() as conn:
        log_message("数据库连接成功 ✓")
    
    # 检查表
    inspector = inspect(app_engine)
    existing_tables = inspector.get_table_names()
    log_message(f"现有表: {existing_tables}")
    
    # 检查关键表
    required_tables = ['users', 'products', 'packing_lists', 'packing_list_items']
    missing_tables = [t for t in required_tables if t not in existing_tables]
    
    if missing_tables:
        log_message(f"警告: 以下必要表不存在: {missing_tables}")
    else:
        log_message("所有必要表都存在 ✓")
    
    # 检查表结构
    for table in existing_tables:
        columns = inspector.get_columns(table)
        log_message(f"\n表 {table} 的结构:")
        for column in columns:
            log_message(f"  - {column['name']}: {column['type']}")
    
except Exception as e:
    log_message(f"检查应用数据库出错: {e}")
    traceback.print_exc()

# 尝试手动创建必要表
log_message("\n" + "=" * 50)
log_message("8. 尝试手动创建表")
log_message("=" * 50)

try:
    # 创建测试数据库
    test_db_path = os.path.join(current_dir, "test_diagnose.db")
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    manual_engine = create_engine(f"sqlite:///{test_db_path}", echo=False)
    
    # 创建用户表
    log_message("创建用户表...")
    with manual_engine.connect() as conn:
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
        conn.commit()
    
    # 确认表创建
    inspector = inspect(manual_engine)
    manual_tables = inspector.get_table_names()
    log_message(f"手动创建的表: {manual_tables}")
    
    if "users" in manual_tables:
        log_message("手动创建表成功 ✓")
        
        # 尝试插入数据
        log_message("尝试插入测试数据...")
        with manual_engine.connect() as conn:
            conn.execute(text("""
            INSERT INTO users (
                username, email, hashed_password, full_name, role, 
                permissions, disabled, created_at, updated_at
            ) VALUES (
                'test_user', 'test@example.com', 'test_password', 'Test User', 'user', 
                '["test:read"]', 0, '2023-01-01T00:00:00', '2023-01-01T00:00:00'
            )
            """))
            conn.commit()
            
            # 测试查询
            result = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            log_message(f"用户数: {result}")
            
            if result > 0:
                log_message("数据插入成功 ✓")
            else:
                log_message("数据插入失败 ✗")
    else:
        log_message("手动创建表失败 ✗")
    
except Exception as e:
    log_message(f"手动创建表出错: {e}")
    traceback.print_exc()

# 添加新的修复功能部分
log_message("\n" + "=" * 50)
log_message("10. 数据库修复工具")
log_message("=" * 50)

def fix_database_issues():
    """修复数据库问题的函数"""
    log_message("开始检查数据库问题...")
    
    # 使用应用的数据库URL或默认URL
    database_url = app_database_url or "sqlite:///./app.db"
    log_message(f"使用数据库URL: {database_url}")
    
    try:
        # 创建数据库引擎
        engine = create_engine(database_url, echo=False)
        
        # 检查数据库连接
        with engine.connect() as conn:
            log_message("数据库连接成功 ✓")
            
            # 检查表是否存在
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            log_message(f"现有表: {existing_tables}")
            
            # 检查users表结构
            if 'users' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('users')]
                log_message(f"users表列: {columns}")
                
                # 检查是否有password列但没有hashed_password列
                if 'password' in columns and 'hashed_password' not in columns:
                    log_message("发现问题: users表有password列但没有hashed_password列")
                    
                    # 询问用户是否修复
                    fix_choice = input("是否修复此问题? (y/n): ").lower()
                    if fix_choice == 'y':
                        log_message("开始修复users表...")
                        
                        # SQLite不支持直接重命名列，需要创建新表
                        with conn.begin():
                            # 创建新表
                            conn.execute(text("""
                            CREATE TABLE users_new (
                                id INTEGER PRIMARY KEY,
                                username VARCHAR NOT NULL,
                                email VARCHAR NOT NULL,
                                hashed_password VARCHAR NOT NULL,
                                full_name VARCHAR,
                                role VARCHAR,
                                permissions VARCHAR,
                                disabled INTEGER DEFAULT 0,
                                created_at VARCHAR,
                                updated_at VARCHAR
                            )
                            """))
                            
                            # 复制数据，将password列的值复制到hashed_password
                            conn.execute(text("""
                            INSERT INTO users_new (id, username, email, hashed_password, full_name, role, permissions, disabled, created_at, updated_at)
                            SELECT id, username, email, password, full_name, role, permissions, disabled, created_at, updated_at FROM users
                            """))
                            
                            # 删除旧表并重命名新表
                            conn.execute(text("DROP TABLE users"))
                            conn.execute(text("ALTER TABLE users_new RENAME TO users"))
                            
                            log_message("已修复: 将password列重命名为hashed_password ✓")
                    else:
                        log_message("用户选择不修复此问题")
                elif 'hashed_password' not in columns:
                    log_message("警告: users表缺少hashed_password列")
                    
                    # 询问用户是否添加列
                    fix_choice = input("是否添加hashed_password列? (y/n): ").lower()
                    if fix_choice == 'y':
                        log_message("开始添加hashed_password列...")
                        
                        # 添加hashed_password列
                        with conn.begin():
                            conn.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR"))
                            log_message("已添加hashed_password列 ✓")
                    else:
                        log_message("用户选择不添加hashed_password列")
                else:
                    log_message("users表结构正常 ✓")
            else:
                log_message("警告: 未找到users表")
                
                # 询问用户是否创建表
                fix_choice = input("是否创建users表? (y/n): ").lower()
                if fix_choice == 'y':
                    log_message("开始创建users表...")
                    
                    # 创建users表
                    with conn.begin():
                        conn.execute(text("""
                        CREATE TABLE users (
                            id INTEGER PRIMARY KEY,
                            username VARCHAR NOT NULL,
                            email VARCHAR NOT NULL,
                            hashed_password VARCHAR NOT NULL,
                            full_name VARCHAR,
                            role VARCHAR,
                            permissions VARCHAR,
                            disabled INTEGER DEFAULT 0,
                            created_at VARCHAR,
                            updated_at VARCHAR
                        )
                        """))
                        
                        log_message("已创建users表 ✓")
                        
                        # 询问是否添加管理员用户
                        add_admin = input("是否添加管理员用户? (y/n): ").lower()
                        if add_admin == 'y':
                            # 从passlib导入密码哈希函数
                            try:
                                from passlib.context import CryptContext
                                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                                admin_password = pwd_context.hash("admin123")
                            except ImportError:
                                log_message("警告: 未安装passlib，使用明文密码")
                                admin_password = "admin123"
                            
                            # 添加管理员用户
                            conn.execute(text("""
                            INSERT INTO users (username, email, hashed_password, full_name, role, permissions, disabled, created_at, updated_at)
                            VALUES ('admin', 'admin@example.com', :password, 'Administrator', 'admin', '["admin"]', 0, :created_at, :updated_at)
                            """), {
                                "password": admin_password,
                                "created_at": datetime.now().isoformat(),
                                "updated_at": datetime.now().isoformat()
                            })
                            
                            log_message("已添加管理员用户 ✓")
                else:
                    log_message("用户选择不创建users表")
            
            # 检查模型与数据库表的一致性
            if app_base:
                log_message("\n检查模型与数据库表的一致性...")
                metadata_tables = list(getattr(app_base.metadata, 'tables', {}).keys())
                
                # 比较元数据表与实际表
                missing_in_db = [t for t in metadata_tables if t not in existing_tables]
                if missing_in_db:
                    log_message(f"警告: 以下表在模型中定义但在数据库中不存在: {missing_in_db}")
                    
                    # 询问用户是否创建缺失的表
                    fix_choice = input("是否创建缺失的表? (y/n): ").lower()
                    if fix_choice == 'y':
                        log_message("开始创建缺失的表...")
                        app_base.metadata.create_all(bind=engine, tables=[
                            app_base.metadata.tables[t] for t in missing_in_db if t in app_base.metadata.tables
                        ])
                        log_message("已创建缺失的表 ✓")
                    else:
                        log_message("用户选择不创建缺失的表")
                else:
                    log_message("所有模型表都存在于数据库中 ✓")
            
            # 检查auth.py中的用户验证逻辑
            log_message("\n检查用户验证逻辑...")
            try:
                import importlib
                
                # 尝试导入auth模块
                auth_modules = [
                    "app.routers.auth",
                    "app.auth.router",
                    "app.crud.user"
                ]
                
                auth_issues = []
                for module_name in auth_modules:
                    try:
                        module = importlib.import_module(module_name)
                        module_src = inspect.getsource(module)
                        
                        # 检查是否使用了password而不是hashed_password
                        if "user.password" in module_src and "verify_password" in module_src:
                            auth_issues.append(f"模块 {module_name} 中使用了user.password而不是user.hashed_password")
                    except (ImportError, AttributeError):
                        pass
                
                if auth_issues:
                    log_message("发现用户验证逻辑问题:")
                    for issue in auth_issues:
                        log_message(f"- {issue}")
                    log_message("请手动修复这些问题，确保所有验证逻辑使用hashed_password字段")
                else:
                    log_message("未发现用户验证逻辑问题 ✓")
            except Exception as e:
                log_message(f"检查用户验证逻辑时出错: {e}")
    
    except Exception as e:
        log_message(f"修复数据库时出错: {e}")
        traceback.print_exc()

# 询问用户是否运行修复工具
run_fix = input("是否运行数据库修复工具? (y/n): ").lower()
if run_fix == 'y':
    fix_database_issues()
else:
    log_message("用户选择不运行修复工具")

# 诊断结论
log_message("\n" + "=" * 50)
log_message("11. 最终诊断结论")
log_message("=" * 50)

# 总结发现的问题
log_message("发现的问题:")
for i, issue in enumerate(issues, 1):
    log_message(f"{i}. {issue}")

# 提供建议
log_message("\n建议:")
log_message("1. 数据库连接问题:")
log_message("   - 确保数据库文件路径正确")
log_message("   - 检查数据库权限")
log_message("   - 确保没有其他进程锁定数据库文件")

log_message("2. 模型注册问题:")
log_message("   - 确保所有模型都导入自同一个Base类")
log_message("   - 避免循环导入问题")
log_message("   - 尝试手动创建表结构作为临时解决方案")

log_message("3. 字段名称不匹配问题:")
log_message("   - 确保模型定义与数据库表结构一致")
log_message("   - 统一使用hashed_password而不是password")
log_message("   - 修改所有验证逻辑，确保使用正确的字段名")

log_message("\n" + "=" * 50)
log_message(f"诊断完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log_message("=" * 50)

# 删除测试数据库
try:
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        log_message("已清理测试数据库")
except:
    pass 