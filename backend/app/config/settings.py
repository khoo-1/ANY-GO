from typing import Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseModel):
    """应用配置"""
    # 数据库配置
    DB_TYPE: str = os.getenv('DB_TYPE', 'sqlite')
    POSTGRES_USER: Optional[str] = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD: Optional[str] = os.getenv('POSTGRES_PASSWORD', 'postgres')
    POSTGRES_HOST: Optional[str] = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT: Optional[int] = int(os.getenv('POSTGRES_PORT', '5432'))
    POSTGRES_DB: Optional[str] = os.getenv('POSTGRES_DB', 'any_go')
    SQLITE_DB: str = os.getenv('SQLITE_DB', 'any_go.db')
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    @property
    def DATABASE_URL(self) -> str:
        """获取数据库连接URL"""
        if self.DB_TYPE == 'postgresql':
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            # SQLite默认配置
            return f"sqlite:///./{self.SQLITE_DB}"

# 创建配置实例
settings = Settings() 