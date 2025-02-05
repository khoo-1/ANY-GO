export type UserRole = 'admin' | 'manager' | 'operator'
export type UserStatus = 'active' | 'inactive'

export interface User {
  id: string
  username: string
  role: UserRole
  status: UserStatus
  permissions: string[]
  lastLoginAt?: string
  createdAt: string
  updatedAt: string
}

export interface UserInfo {
  id: string
  username: string
  role: UserRole
  permissions: string[]
} 