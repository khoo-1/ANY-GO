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
        let user = req.user;
        console.log('操作日志 - 当前操作:', { module, action });
        
        // 对于登录操作，从响应数据中获取用户信息
        if (action === 'login' && data) {
          console.log('操作日志 - 登录响应数据:', data);
          const responseData = JSON.parse(data);
          console.log('操作日志 - 解析后的响应数据:', responseData);
          if (responseData.data && responseData.data.user) {
            user = responseData.data.user;
            console.log('操作日志 - 从响应中获取到用户:', user);
          }
        }

        if (!user) {
          console.warn('未找到用户信息，跳过日志记录');
          return originalSend.call(this, data);
        }

        const logEntry = {
          userId: user._id || user.id,
          username: user.username,
          module,
          action,
          description: `${user.username} 执行了 ${module} 模块的 ${action} 操作`,
          details: {
            method: req.method,
            url: req.originalUrl,
            body: req.body,
            ip: req.ip,
            userAgent: req.get('user-agent')
          },
          status: res.statusCode,
          response: data
        };

        console.log('操作日志 - 准备保存日志:', logEntry);
        const operationLog = new OperationLog(logEntry);
        await operationLog.save();
        console.log('操作日志 - 日志保存成功');
      } catch (error) {
        console.error('记录操作日志失败:', error);
      }
      return originalSend.call(this, data);
    };
    next();
  };
};

// 生成 JWT Token
exports.generateToken = (userId) => {
  return jwt.sign({ userId }, JWT_SECRET, { expiresIn: '24h' });
}; 