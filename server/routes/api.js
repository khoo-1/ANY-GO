const express = require('express');
const router = express.Router();
const { verifyToken, checkPermission, logOperation } = require('../middleware/auth');
const authController = require('../controllers/authController');
const userController = require('../controllers/userController');
const backupController = require('../controllers/backupController');
const logController = require('../controllers/logController');

// 认证相关路由
router.post('/auth/login', logOperation('users', 'login'), authController.login);
router.post('/auth/register', verifyToken, checkPermission('users:write'), logOperation('users', 'create'), authController.register);
router.get('/auth/current-user', verifyToken, authController.getCurrentUser);

// 用户管理路由
router.get('/users', verifyToken, checkPermission('users:read'), logOperation('users', 'read'), userController.list);
router.put('/users/:id', verifyToken, checkPermission('users:write'), logOperation('users', 'update'), userController.update);
router.delete('/users/:id', verifyToken, checkPermission('users:delete'), logOperation('users', 'delete'), userController.delete);
router.post('/users/:id/reset-password', verifyToken, checkPermission('users:write'), logOperation('users', 'update'), userController.resetPassword);

// 备份管理路由
router.post('/backups', verifyToken, checkPermission('system:backup'), logOperation('system', 'backup'), backupController.createBackup);
router.get('/backups', verifyToken, checkPermission('system:backup'), logOperation('system', 'read'), backupController.listBackups);
router.post('/backups/:id/restore', verifyToken, checkPermission('system:backup'), logOperation('system', 'update'), backupController.restoreBackup);
router.delete('/backups/:id', verifyToken, checkPermission('system:backup'), logOperation('system', 'delete'), backupController.deleteBackup);

// 日志管理路由
router.get('/logs', verifyToken, checkPermission('users:read'), logOperation('system', 'read'), logController.list);
router.get('/logs/statistics', verifyToken, checkPermission('users:read'), logOperation('system', 'read'), logController.getStatistics);
router.delete('/logs', verifyToken, checkPermission('users:delete'), logOperation('system', 'delete'), logController.deleteOldLogs);

module.exports = router; 