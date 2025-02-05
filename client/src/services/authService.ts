import { http } from '../utils/http';
import { User } from '../types/api';

export interface LoginParams {
  username: string;
  password: string;
}

export interface LoginResponse {
  code: number;
  data: {
    token: string;
    user: User;
  };
  message: string;
}

export interface RegisterParams {
  username: string;
  password: string;
  role?: string;
}

const authService = {
  login: async (params: { username: string; password: string }): Promise<LoginResponse> => {
    const response = await http.post<LoginResponse>('/api/auth/login', params);
    return response.data;
  },

  register: async (params: RegisterParams): Promise<User> => {
    const response = await http.post<{ user: User }>('/api/auth/register', params);
    return response.data.user;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await http.get<User>('/api/auth/current-user');
    return response.data;
  },

  logout: async () => {
    try {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    } catch (error) {
      console.error('清除用户数据失败:', error);
    }
  },

  getToken: (): string | null => {
    try {
      return localStorage.getItem('token');
    } catch (error) {
      console.error('获取token失败:', error);
      return null;
    }
  },

  getUser: (): User | null => {
    try {
      const userStr = localStorage.getItem('user');
      if (!userStr) return null;
      const user = JSON.parse(userStr);
      return user && typeof user === 'object' ? user : null;
    } catch (error) {
      console.error('获取用户数据失败:', error);
      localStorage.removeItem('user');
      return null;
    }
  },

  isAuthenticated: (): boolean => {
    try {
      return !!localStorage.getItem('token');
    } catch (error) {
      console.error('检查认证状态失败:', error);
      return false;
    }
  },

  hasPermission: (permission: string): boolean => {
    try {
      const user = authService.getUser();
      if (!user) return false;
      if (user.role === 'admin') return true;
      return Array.isArray(user.permissions) && user.permissions.includes(permission);
    } catch (error) {
      console.error('检查权限失败:', error);
      return false;
    }
  }
};

export default authService; 