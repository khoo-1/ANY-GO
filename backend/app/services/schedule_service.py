from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional

from ..database import SessionLocal
from ..models.operation_log import OperationLog
from ..models.user import User
from .backup_service import backup_service, BackupType

class ScheduleService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}

    async def init(self):
        """初始化定时任务"""
        # 每天凌晨3点执行全量备份
        self.schedule_backup("0 3 * * *", BackupType.FULL)
        
        # 每6小时执行一次增量备份
        self.schedule_backup("0 */6 * * *", BackupType.PRODUCTS)
        self.schedule_backup("0 */6 * * *", BackupType.PACKING_LISTS)
        
        # 每30天清理一次过期日志
        self.schedule_clean_logs("0 4 */30 * *")
        
        # 启动调度器
        self.scheduler.start()

    def schedule_backup(self, cron: str, backup_type: BackupType):
        """调度备份任务"""
        job_id = f"backup_{backup_type}"
        
        async def backup_job():
            try:
                print(f"开始执行{backup_type}备份任务...")
                db = SessionLocal()
                try:
                    # 使用系统管理员账号执行备份
                    admin = db.query(User).filter(User.role == "admin").first()
                    if not admin:
                        raise ValueError("未找到管理员账号")
                    
                    await backup_service.create_backup(
                        db=db,
                        backup_type=backup_type,
                        user_id=admin.id,
                        description=f"定时{backup_type}备份"
                    )
                    print(f"{backup_type}备份任务执行完成")
                    
                finally:
                    db.close()
                    
            except Exception as e:
                print(f"{backup_type}备份任务执行失败:", str(e))
        
        self.scheduler.add_job(
            backup_job,
            CronTrigger.from_crontab(cron),
            id=job_id,
            replace_existing=True
        )
        self.jobs[job_id] = cron
        print(f"已调度{backup_type}备份任务: {cron}")

    def schedule_clean_logs(self, cron: str, days: int = 30):
        """调度日志清理任务"""
        job_id = "clean_logs"
        
        async def clean_logs_job():
            try:
                print("开始执行日志清理任务...")
                db = SessionLocal()
                try:
                    # 计算过期时间
                    expire_date = datetime.utcnow() - timedelta(days=days)
                    
                    # 删除过期日志
                    result = db.query(OperationLog).filter(
                        OperationLog.created_at < expire_date
                    ).delete()
                    
                    db.commit()
                    print(f"日志清理任务完成，删除了 {result} 条记录")
                    
                finally:
                    db.close()
                    
            except Exception as e:
                print("日志清理任务执行失败:", str(e))
        
        self.scheduler.add_job(
            clean_logs_job,
            CronTrigger.from_crontab(cron),
            id=job_id,
            replace_existing=True
        )
        self.jobs[job_id] = cron
        print(f"已调度日志清理任务: {cron}")

    def cancel_all_jobs(self):
        """取消所有定时任务"""
        for job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            print(f"已取消定时任务: {job_id}")
        self.jobs.clear()

    def reschedule_job(self, job_id: str, cron: str):
        """重新调度任务"""
        if job_id in self.jobs:
            self.scheduler.reschedule_job(
                job_id,
                trigger=CronTrigger.from_crontab(cron)
            )
            self.jobs[job_id] = cron
            print(f"已重新调度任务 {job_id}: {cron}")

schedule_service = ScheduleService() 