import sys
from pathlib import Path
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app.models import Base
from app.config import settings
from app.security import get_password_hash
from app.models import User

async def init_db():
    # 创建异步数据库引擎
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 创建异步会话
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # 创建管理员用户
    async with async_session() as session:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        session.add(admin_user)
        await session.commit()

    print("数据库初始化完成！")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())