import os
import subprocess
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def run_migrations():
    """运行数据库迁移"""
    print("开始运行数据库迁移...")
    
    # 确保数据库URL已设置
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("环境变量DATABASE_URL未设置")
    
    try:
        # 运行Alembic迁移
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("数据库迁移成功完成")
    except subprocess.CalledProcessError as e:
        print(f"迁移过程中出错: {e}")
        raise
    except Exception as e:
        print(f"发生未知错误: {e}")
        raise

if __name__ == "__main__":
    run_migrations() 