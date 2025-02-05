import request from '../utils/request'
import type { User } from '../types/user'

export interface UserQuery {
  page?: number
  pageSize?: number
  keyword?: string
  role?: string
  status?: string
}

export interface UserCreateParams {
  username: string
  password: string
  role: string
  status: string
}

export interface UserUpdateParams {
  username?: string
  role?: string
  status?: string
}

export interface ResetPasswordParams {
  newPassword: string
}

export default {
  // 获取用户列表
  list(params: UserQuery) {
    return request.get<{
      items: User[]
      pagination: {
        total: number
        current: number
        pageSize: number
      }
    }>('/api/users', { params })
  },

  // 创建用户
  create(data: UserCreateParams) {
    return request.post<User>('/api/users', data)
  },

  // 更新用户
  update(id: string, data: UserUpdateParams) {
    return request.put<User>(`/api/users/${id}`, data)
  },

  // 删除用户
  delete(id: string) {
    return request.delete(`/api/users/${id}`)
  },

  // 重置密码
  resetPassword(id: string, data: ResetPasswordParams) {
    return request.post(`/api/users/${id}/reset-password`, data)
  }
} 