# 认证模块初始化文件

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# 配置密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 配置OAuth2认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 密码哈希函数
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 验证密码函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)