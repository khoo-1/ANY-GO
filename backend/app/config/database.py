from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os

class DatabaseSettings(BaseSettings):
    """数据库配置"""
    # 数据库类型：sqlite或postgresql
    DB_TYPE: str = os.getenv('DB_TYPE', 'sqlite')
    
    # PostgreSQL配置
    POSTGRES_USER: Optional[str] = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD: Optional[str] = os.getenv('POSTGRES_PASSWORD', 'postgres')
    POSTGRES_HOST: Optional[str] = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT: Optional[int] = int(os.getenv('POSTGRES_PORT', '5432'))
    POSTGRES_DB: Optional[str] = os.getenv('POSTGRES_DB', 'any_go')
    
    # SQLite配置
    SQLITE_DB: str = os.getenv('SQLITE_DB', 'any_go.db')
    
    @property
    def DATABASE_URL(self) -> str:
        """获取数据库连接URL"""
        if self.DB_TYPE == 'postgresql':
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            # SQLite默认配置
            return f"sqlite:///./{self.SQLITE_DB}"
    
    model_config = ConfigDict(env_file='.env', extra='allow')

# 创建数据库配置实例
database_settings = DatabaseSettings()