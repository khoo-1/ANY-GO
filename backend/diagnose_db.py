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

# 诊断结论
log_message("\n" + "=" * 50)
log_message("9. 诊断结论")
log_message("=" * 50)

issues = []

# 检查编码问题
if sys.stdout.encoding != 'utf-8':
    issues.append("控制台编码不是UTF-8，中文和特殊字符可能显示乱码")

# 检查数据库连接
try:
    with create_engine(app_database_url, echo=False).connect() as conn:
        pass
except:
    issues.append("无法连接到应用数据库")

# 检查模型注册
if app_base and model_tables:
    tables_in_metadata = list(getattr(app_base.metadata, 'tables', {}).keys())
    missing_tables = [t for t in model_tables if t not in tables_in_metadata]
    if missing_tables:
        issues.append(f"模型表未正确注册到Base.metadata: {missing_tables}")

# 输出结论
if issues:
    log_message("\n发现以下问题:")
    for i, issue in enumerate(issues, 1):
        log_message(f"{i}. {issue}")
    
    log_message("\n解决方案建议:")
    
    # 编码问题解决方案
    if "控制台编码不是UTF-8" in issues[0]:
        log_message("1. 编码问题:")
        log_message("   - 在PowerShell中运行: chcp 65001")
        log_message("   - 设置环境变量: $env:PYTHONIOENCODING = 'utf-8'")
        log_message("   - 在脚本开头添加: # -*- coding: utf-8 -*-")
    
    # 模型注册问题解决方案
    if any("模型表未正确注册" in issue for issue in issues):
        log_message("2. 模型注册问题:")
        log_message("   - 确保所有模型都导入自同一个Base类")
        log_message("   - 避免循环导入问题")
        log_message("   - 尝试手动创建表结构作为临时解决方案")
    
    # 数据库连接问题解决方案
    if any("无法连接到应用数据库" in issue for issue in issues):
        log_message("3. 数据库连接问题:")
        log_message("   - 检查DATABASE_URL是否正确")
        log_message("   - 确保数据库文件路径可写")
        log_message("   - 检查SQLite版本兼容性")
else:
    log_message("诊断未发现明显问题 ✓")
    log_message("如果仍有问题，建议:")
    log_message("1. 备份并删除现有数据库文件，重新初始化")
    log_message("2. 检查应用代码中的表结构定义")
    log_message("3. 查看应用日志获取更多错误信息")

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