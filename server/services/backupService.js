const fs = require('fs').promises;
const path = require('path');
const archiver = require('archiver');
const mongoose = require('mongoose');
const Backup = require('../models/Backup');
const Product = require('../models/Product');
const PackingList = require('../models/PackingList');

class BackupService {
  constructor() {
    this.backupDir = path.join(__dirname, '../backups');
  }

  async init() {
    try {
      await fs.mkdir(this.backupDir, { recursive: true });
    } catch (error) {
      console.error('创建备份目录失败:', error);
      throw error;
    }
  }

  async createBackup(type, userId) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `backup-${type}-${timestamp}.zip`;
    const filepath = path.join(this.backupDir, filename);

    const backup = await Backup.create({
      filename,
      size: 0,
      type,
      path: filepath,
      createdBy: userId
    });

    try {
      const output = fs.createWriteStream(filepath);
      const archive = archiver('zip', {
        zlib: { level: 9 }
      });

      archive.pipe(output);

      // 根据类型备份不同的数据
      switch (type) {
        case 'products':
          await this.backupProducts(archive);
          break;
        case 'packingLists':
          await this.backupPackingLists(archive);
          break;
        case 'full':
          await this.backupProducts(archive);
          await this.backupPackingLists(archive);
          break;
      }

      await archive.finalize();

      const stats = await fs.stat(filepath);
      backup.size = stats.size;
      backup.status = 'completed';
      backup.completedAt = new Date();
      await backup.save();

      return backup;
    } catch (error) {
      backup.status = 'failed';
      backup.error = error.message;
      await backup.save();
      throw error;
    }
  }

  async backupProducts(archive) {
    const products = await Product.find({});
    archive.append(JSON.stringify(products, null, 2), { name: 'products.json' });
  }

  async backupPackingLists(archive) {
    const packingLists = await PackingList.find({});
    archive.append(JSON.stringify(packingLists, null, 2), { name: 'packingLists.json' });
  }

  async restoreBackup(backupId) {
    const backup = await Backup.findById(backupId);
    if (!backup) {
      throw new Error('备份不存在');
    }

    const fileContent = await fs.readFile(backup.path);
    const data = JSON.parse(fileContent);

    const session = await mongoose.startSession();
    try {
      await session.withTransaction(async () => {
        switch (backup.type) {
          case 'products':
            await Product.deleteMany({}, { session });
            await Product.insertMany(data.products, { session });
            break;
          case 'packingLists':
            await PackingList.deleteMany({}, { session });
            await PackingList.insertMany(data.packingLists, { session });
            break;
          case 'full':
            await Product.deleteMany({}, { session });
            await PackingList.deleteMany({}, { session });
            await Product.insertMany(data.products, { session });
            await PackingList.insertMany(data.packingLists, { session });
            break;
        }
      });
    } finally {
      await session.endSession();
    }
  }

  async listBackups(query = {}) {
    return Backup.find(query)
      .sort({ createdAt: -1 })
      .populate('createdBy', 'username');
  }

  async deleteBackup(backupId) {
    const backup = await Backup.findById(backupId);
    if (!backup) {
      throw new Error('备份不存在');
    }

    try {
      await fs.unlink(backup.path);
    } catch (error) {
      console.error('删除备份文件失败:', error);
    }

    await backup.deleteOne();
  }
}

module.exports = new BackupService(); 