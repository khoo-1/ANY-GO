import http from '../utils/http';
import { User } from '../types/api';

export interface LoginParams {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface RegisterParams {
  username: string;
  password: string;
  role?: string;
}

const authService = {
  login: async (params: LoginParams): Promise<LoginResponse> => {
    const response = await http.post<LoginResponse>('/api/auth/login', params);
    const { token, user } = response.data;
    
    // 保存 token 到 localStorage
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    
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

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getToken: (): string | null => {
    return localStorage.getItem('token');
  },

  getUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  hasPermission: (permission: string): boolean => {
    const user = authService.getUser();
    if (!user) return false;
    if (user.role === 'admin') return true;
    return user.permissions.includes(permission);
  }
};

export default authService; 