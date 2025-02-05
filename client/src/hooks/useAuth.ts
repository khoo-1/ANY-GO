import { useState, useEffect } from 'react';
import { message } from 'antd';
import { User } from '../types/api';

export interface AuthHook {
  user: User | null;
  login: (userData: User, token: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

export const useAuth = (): AuthHook => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    try {
      // 从localStorage获取用户信息
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const parsedUser = JSON.parse(storedUser);
        if (parsedUser && typeof parsedUser === 'object') {
          setUser(parsedUser);
        }
      }
    } catch (error) {
      console.error('解析用户数据失败:', error);
      // 清除无效的数据
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    }
  }, []);

  const login = (userData: User, token: string) => {
    try {
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('token', token);
      message.success('登录成功');
    } catch (error) {
      console.error('保存用户数据失败:', error);
      message.error('登录失败：无法保存用户数据');
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    message.success('已退出登录');
  };

  return {
    user,
    login,
    logout,
    isAuthenticated: !!user
  };
}; 