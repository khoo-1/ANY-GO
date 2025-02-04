const OperationLog = require('../models/OperationLog');

exports.list = async (req, res) => {
  try {
    const {
      page = 1,
      pageSize = 10,
      module,
      action,
      username,
      status,
      startDate,
      endDate
    } = req.query;

    const query = {};

    if (module) query.module = module;
    if (action) query.action = action;
    if (username) query.username = new RegExp(username, 'i');
    if (status) query.status = status;
    if (startDate || endDate) {
      query.createdAt = {};
      if (startDate) query.createdAt.$gte = new Date(startDate);
      if (endDate) query.createdAt.$lte = new Date(endDate);
    }

    const total = await OperationLog.countDocuments(query);
    const logs = await OperationLog.find(query)
      .sort({ createdAt: -1 })
      .skip((page - 1) * pageSize)
      .limit(parseInt(pageSize))
      .populate('userId', 'username');

    res.json({
      items: logs,
      pagination: {
        total,
        current: parseInt(page),
        pageSize: parseInt(pageSize)
      }
    });
  } catch (error) {
    console.error('获取操作日志失败:', error);
    res.status(500).json({ message: '获取操作日志失败' });
  }
};

exports.getStatistics = async (req, res) => {
  try {
    const { startDate, endDate } = req.query;
    const query = {};

    if (startDate || endDate) {
      query.createdAt = {};
      if (startDate) query.createdAt.$gte = new Date(startDate);
      if (endDate) query.createdAt.$lte = new Date(endDate);
    }

    // 获取模块操作统计
    const moduleStats = await OperationLog.aggregate([
      { $match: query },
      { $group: {
        _id: '$module',
        count: { $sum: 1 }
      }},
      { $sort: { count: -1 } }
    ]);

    // 获取操作类型统计
    const actionStats = await OperationLog.aggregate([
      { $match: query },
      { $group: {
        _id: '$action',
        count: { $sum: 1 }
      }},
      { $sort: { count: -1 } }
    ]);

    // 获取用户操作统计
    const userStats = await OperationLog.aggregate([
      { $match: query },
      { $group: {
        _id: '$username',
        count: { $sum: 1 }
      }},
      { $sort: { count: -1 } },
      { $limit: 10 }
    ]);

    res.json({
      moduleStats,
      actionStats,
      userStats
    });
  } catch (error) {
    console.error('获取操作统计失败:', error);
    res.status(500).json({ message: '获取操作统计失败' });
  }
};

exports.deleteOldLogs = async (req, res) => {
  try {
    const { days = 30 } = req.body;
    const date = new Date();
    date.setDate(date.getDate() - days);

    const result = await OperationLog.deleteMany({
      createdAt: { $lt: date }
    });

    res.json({
      message: `成功删除 ${result.deletedCount} 条过期日志`,
      deletedCount: result.deletedCount
    });
  } catch (error) {
    console.error('删除过期日志失败:', error);
    res.status(500).json({ message: '删除过期日志失败' });
  }
}; 