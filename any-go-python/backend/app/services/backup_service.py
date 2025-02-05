import os
import json
import shutil
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
import aiofiles
from fastapi import UploadFile

from ..models.backup import Backup, BackupType, BackupStatus
from ..models.product import Product
from ..models.packing_list import PackingList
from ..config import settings

class BackupService:
    def __init__(self):
        self.backup_dir = os.path.join(os.getcwd(), "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    async def create_backup(
        self,
        db: Session,
        backup_type: BackupType,
        user_id: int,
        description: Optional[str] = None
    ) -> Backup:
        """创建备份"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{backup_type}_{timestamp}.json"
        filepath = os.path.join(self.backup_dir, filename)

        # 创建备份记录
        backup = Backup(
            filename=filename,
            size=0,
            type=backup_type,
            path=filepath,
            description=description,
            created_by=user_id
        )
        db.add(backup)
        db.commit()

        try:
            # 根据类型备份不同的数据
            data = {}
            if backup_type == BackupType.PRODUCTS or backup_type == BackupType.FULL:
                products = db.query(Product).all()
                data["products"] = [product.__dict__ for product in products]

            if backup_type == BackupType.PACKING_LISTS or backup_type == BackupType.FULL:
                packing_lists = db.query(PackingList).all()
                data["packing_lists"] = [pl.__dict__ for pl in packing_lists]

            # 写入备份文件
            async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))

            # 更新备份状态
            file_size = os.path.getsize(filepath)
            backup.size = file_size
            backup.status = BackupStatus.COMPLETED
            backup.completed_at = datetime.utcnow()
            db.commit()

            return backup

        except Exception as e:
            backup.status = BackupStatus.FAILED
            backup.error = str(e)
            db.commit()
            raise

    async def restore_backup(
        self,
        db: Session,
        backup_id: int
    ) -> None:
        """恢复备份"""
        backup = db.query(Backup).filter(Backup.id == backup_id).first()
        if not backup:
            raise ValueError("备份不存在")

        if backup.status != BackupStatus.COMPLETED:
            raise ValueError("备份未完成，无法恢复")

        try:
            # 读取备份文件
            async with aiofiles.open(backup.path, "r", encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)

            # 根据备份类型恢复数据
            if backup.type in [BackupType.PRODUCTS, BackupType.FULL]:
                # 清空现有数据
                db.query(Product).delete()
                # 恢复产品数据
                for product_data in data.get("products", []):
                    product = Product(**product_data)
                    db.add(product)

            if backup.type in [BackupType.PACKING_LISTS, BackupType.FULL]:
                # 清空现有数据
                db.query(PackingList).delete()
                # 恢复装箱单数据
                for pl_data in data.get("packing_lists", []):
                    packing_list = PackingList(**pl_data)
                    db.add(packing_list)

            db.commit()

        except Exception as e:
            db.rollback()
            raise ValueError(f"恢复备份失败: {str(e)}")

    def list_backups(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10,
        backup_type: Optional[BackupType] = None
    ) -> List[Backup]:
        """获取备份列表"""
        query = db.query(Backup)
        if backup_type:
            query = query.filter(Backup.type == backup_type)
        return query.order_by(Backup.created_at.desc()).offset(skip).limit(limit).all()

    async def delete_backup(
        self,
        db: Session,
        backup_id: int
    ) -> None:
        """删除备份"""
        backup = db.query(Backup).filter(Backup.id == backup_id).first()
        if not backup:
            raise ValueError("备份不存在")

        try:
            # 删除备份文件
            if os.path.exists(backup.path):
                os.remove(backup.path)

            # 删除数据库记录
            db.delete(backup)
            db.commit()

        except Exception as e:
            db.rollback()
            raise ValueError(f"删除备份失败: {str(e)}")

backup_service = BackupService() 