import os
from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app.database import Base
from app.models import User, Product, PackingList, PackingListItem

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 从环境变量中获取数据库连接URL
database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
config.set_main_option("sqlalchemy.url", database_url)

# 如果使用 SQLite，添加特殊配置
if database_url.startswith("sqlite"):
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    from sqlite3 import Connection as SQLite3Connection

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, SQLite3Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # 获取配置
    configuration = config.get_section(config.config_ini_section, {})
    
    # 如果使用 SQLite，添加特殊配置
    if config.get_main_option("sqlalchemy.url").startswith("sqlite"):
        configuration["sqlalchemy.connect_args"] = {"check_same_thread": False}
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
