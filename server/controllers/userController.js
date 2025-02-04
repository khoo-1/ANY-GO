const User = require('../models/User');

exports.list = async (req, res) => {
  try {
    const { page = 1, pageSize = 10, status, role } = req.query;
    const query = {};

    if (status) query.status = status;
    if (role) query.role = role;

    const total = await User.countDocuments(query);
    const users = await User.find(query)
      .select('-password')
      .sort({ createdAt: -1 })
      .skip((page - 1) * pageSize)
      .limit(parseInt(pageSize));

    res.json({
      items: users,
      pagination: {
        total,
        current: parseInt(page),
        pageSize: parseInt(pageSize)
      }
    });
  } catch (error) {
    console.error('获取用户列表失败:', error);
    res.status(500).json({ message: '获取用户列表失败' });
  }
};

exports.update = async (req, res) => {
  try {
    const { id } = req.params;
    const { username, role, status, permissions } = req.body;

    const user = await User.findById(id);
    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }

    // 更新用户信息
    if (username) user.username = username;
    if (role) {
      user.role = role;
      // 如果更改了角色，重置权限
      user.permissions = user.getDefaultPermissions();
    }
    if (status) user.status = status;
    if (permissions) user.permissions = permissions;

    await user.save();
    res.json({ message: '更新成功', user: user.toObject({ hide: 'password' }) });
  } catch (error) {
    console.error('更新用户失败:', error);
    res.status(500).json({ message: '更新用户失败' });
  }
};

exports.delete = async (req, res) => {
  try {
    const { id } = req.params;
    const user = await User.findById(id);

    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }

    if (user.role === 'admin') {
      return res.status(403).json({ message: '不能删除管理员账号' });
    }

    await user.deleteOne();
    res.json({ message: '删除成功' });
  } catch (error) {
    console.error('删除用户失败:', error);
    res.status(500).json({ message: '删除用户失败' });
  }
};

exports.resetPassword = async (req, res) => {
  try {
    const { id } = req.params;
    const { newPassword } = req.body;

    const user = await User.findById(id);
    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }

    user.password = newPassword;
    await user.save();

    res.json({ message: '密码重置成功' });
  } catch (error) {
    console.error('重置密码失败:', error);
    res.status(500).json({ message: '重置密码失败' });
  }
}; 