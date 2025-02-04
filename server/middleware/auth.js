const jwt = require('jsonwebtoken');
const User = require('../models/User');
const OperationLog = require('../models/OperationLog');

// JWT 密钥
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

// 验证 JWT Token
exports.verifyToken = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      return res.status(401).json({ message: '未提供认证令牌' });
    }

    const decoded = jwt.verify(token, JWT_SECRET);
    const user = await User.findById(decoded.userId);

    if (!user || user.status !== 'active') {
      return res.status(401).json({ message: '用户不存在或已被禁用' });
    }

    req.user = user;
    next();
  } catch (error) {
    return res.status(401).json({ message: '无效的认证令牌' });
  }
};

// 检查权限
exports.checkPermission = (permission) => {
  return async (req, res, next) => {
    try {
      const user = req.user;
      if (!user) {
        return res.status(401).json({ message: '未认证的用户' });
      }

      if (user.role === 'admin') {
        return next();
      }

      if (!user.permissions.includes(permission)) {
        return res.status(403).json({ message: '没有操作权限' });
      }

      next();
    } catch (error) {
      next(error);
    }
  };
};

// 记录操作日志
exports.logOperation = (module, action) => {
  return async (req, res, next) => {
    const originalSend = res.send;
    res.send = async function (data) {
      res.send = originalSend;
      try {
        const logEntry = {
          userId: req.user._id,
          username: req.user.username,
          module,
          action,
          description: `${req.user.username} 执行了 ${module} 模块的 ${action} 操作`,
          details: {
            method: req.method,
            url: req.originalUrl,
            body: req.body,
            params: req.params,
            query: req.query
          },
          ip: req.ip,
          userAgent: req.get('user-agent'),
          status: res.statusCode >= 400 ? 'failure' : 'success'
        };

        await OperationLog.create(logEntry);
      } catch (error) {
        console.error('记录操作日志失败:', error);
      }
      
      return res.send(data);
    };
    next();
  };
};

// 生成 JWT Token
exports.generateToken = (userId) => {
  return jwt.sign({ userId }, JWT_SECRET, { expiresIn: '24h' });
}; 