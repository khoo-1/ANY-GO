import http from '../utils/http';
import { User, ListResponse } from '../types/api';

export interface UserQuery {
  page?: number;
  pageSize?: number;
  status?: string;
  role?: string;
}

export interface UpdateUserParams {
  username?: string;
  role?: string;
  status?: string;
  permissions?: string[];
}

const userService = {
  list: async (params: UserQuery): Promise<ListResponse<User>> => {
    const response = await http.get<ListResponse<User>>('/api/users', { params });
    return response.data;
  },

  update: async (id: string, params: UpdateUserParams): Promise<User> => {
    const response = await http.put<{ user: User }>(`/api/users/${id}`, params);
    return response.data.user;
  },

  delete: async (id: string): Promise<void> => {
    await http.delete(`/api/users/${id}`);
  },

  resetPassword: async (id: string, newPassword: string): Promise<void> => {
    await http.post(`/api/users/${id}/reset-password`, { newPassword });
  }
};

export default userService; 