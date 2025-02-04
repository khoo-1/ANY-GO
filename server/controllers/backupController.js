const backupService = require('../services/backupService');

exports.createBackup = async (req, res) => {
  try {
    const { type = 'full' } = req.body;
    const backup = await backupService.createBackup(type, req.user._id);
    res.json({ message: '备份创建成功', backup });
  } catch (error) {
    console.error('创建备份失败:', error);
    res.status(500).json({ message: '创建备份失败' });
  }
};

exports.listBackups = async (req, res) => {
  try {
    const { page = 1, pageSize = 10, type, status } = req.query;
    const query = {};

    if (type) query.type = type;
    if (status) query.status = status;

    const total = await backupService.countBackups(query);
    const backups = await backupService.listBackups(query)
      .skip((page - 1) * pageSize)
      .limit(parseInt(pageSize));

    res.json({
      items: backups,
      pagination: {
        total,
        current: parseInt(page),
        pageSize: parseInt(pageSize)
      }
    });
  } catch (error) {
    console.error('获取备份列表失败:', error);
    res.status(500).json({ message: '获取备份列表失败' });
  }
};

exports.restoreBackup = async (req, res) => {
  try {
    const { id } = req.params;
    await backupService.restoreBackup(id);
    res.json({ message: '恢复备份成功' });
  } catch (error) {
    console.error('恢复备份失败:', error);
    res.status(500).json({ message: '恢复备份失败' });
  }
};

exports.deleteBackup = async (req, res) => {
  try {
    const { id } = req.params;
    await backupService.deleteBackup(id);
    res.json({ message: '删除备份成功' });
  } catch (error) {
    console.error('删除备份失败:', error);
    res.status(500).json({ message: '删除备份失败' });
  }
}; 