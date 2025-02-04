const schedule = require('node-schedule');
const backupService = require('./backupService');
const User = require('../models/User');

class ScheduleService {
  constructor() {
    this.jobs = new Map();
  }

  // 初始化定时任务
  async init() {
    // 每天凌晨3点执行全量备份
    this.scheduleBackup('0 3 * * *', 'full');
    
    // 每6小时执行一次增量备份
    this.scheduleBackup('0 */6 * * *', 'products');
    this.scheduleBackup('0 */6 * * *', 'packingLists');

    // 每30天清理一次过期日志
    this.scheduleCleanLogs('0 4 */30 * *');
  }

  // 调度备份任务
  scheduleBackup(cronExpression, type) {
    const jobName = `backup-${type}`;
    const job = schedule.scheduleJob(jobName, cronExpression, async () => {
      try {
        console.log(`开始执行${type}备份任务...`);
        // 使用系统管理员账号执行备份
        const admin = await User.findOne({ role: 'admin' });
        if (!admin) {
          throw new Error('未找到管理员账号');
        }
        await backupService.createBackup(type, admin._id);
        console.log(`${type}备份任务执行完成`);
      } catch (error) {
        console.error(`${type}备份任务执行失败:`, error);
      }
    });

    this.jobs.set(jobName, job);
    console.log(`已调度${type}备份任务: ${cronExpression}`);
  }

  // 调度日志清理任务
  scheduleCleanLogs(cronExpression) {
    const jobName = 'clean-logs';
    const job = schedule.scheduleJob(jobName, cronExpression, async () => {
      try {
        console.log('开始执行日志清理任务...');
        const OperationLog = require('../models/OperationLog');
        const date = new Date();
        date.setDate(date.getDate() - 30);

        const result = await OperationLog.deleteMany({
          createdAt: { $lt: date }
        });

        console.log(`日志清理任务完成，删除了 ${result.deletedCount} 条记录`);
      } catch (error) {
        console.error('日志清理任务执行失败:', error);
      }
    });

    this.jobs.set(jobName, job);
    console.log(`已调度日志清理任务: ${cronExpression}`);
  }

  // 取消所有定时任务
  cancelAllJobs() {
    for (const [name, job] of this.jobs) {
      job.cancel();
      console.log(`已取消定时任务: ${name}`);
    }
    this.jobs.clear();
  }

  // 重新调度任务
  reschedule(jobName, cronExpression) {
    const job = this.jobs.get(jobName);
    if (job) {
      job.reschedule(cronExpression);
      console.log(`已重新调度任务 ${jobName}: ${cronExpression}`);
    }
  }
}

module.exports = new ScheduleService(); 