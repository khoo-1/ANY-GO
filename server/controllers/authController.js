const User = require('../models/User');
const { generateToken } = require('../middleware/auth');

exports.login = async (req, res) => {
  try {
    const { username, password } = req.body;
    
    const user = await User.findOne({ username });
    if (!user) {
      return res.status(401).json({ message: '用户名或密码错误' });
    }

    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      return res.status(401).json({ message: '用户名或密码错误' });
    }

    if (user.status !== 'active') {
      return res.status(403).json({ message: '账号已被禁用' });
    }

    // 更新最后登录时间
    user.lastLoginAt = new Date();
    await user.save();

    const token = generateToken(user._id);
    res.json({
      token,
      user: {
        id: user._id,
        username: user.username,
        role: user.role,
        permissions: user.permissions
      }
    });
  } catch (error) {
    console.error('登录失败:', error);
    res.status(500).json({ message: '登录失败' });
  }
};

exports.register = async (req, res) => {
  try {
    const { username, password, role } = req.body;

    // 检查用户名是否已存在
    const existingUser = await User.findOne({ username });
    if (existingUser) {
      return res.status(400).json({ message: '用户名已存在' });
    }

    // 创建新用户
    const user = new User({
      username,
      password,
      role: role || 'operator'
    });

    // 设置默认权限
    user.permissions = user.getDefaultPermissions();
    await user.save();

    res.status(201).json({
      message: '注册成功',
      user: {
        id: user._id,
        username: user.username,
        role: user.role,
        permissions: user.permissions
      }
    });
  } catch (error) {
    console.error('注册失败:', error);
    res.status(500).json({ message: '注册失败' });
  }
};

exports.getCurrentUser = async (req, res) => {
  try {
    const user = await User.findById(req.user._id).select('-password');
    res.json(user);
  } catch (error) {
    console.error('获取当前用户信息失败:', error);
    res.status(500).json({ message: '获取用户信息失败' });
  }
}; 