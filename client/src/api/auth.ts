import request from '../utils/request'

interface LoginData {
  username: string
  password: string
}

interface LoginResponse {
  access_token: string
  token_type: string
}

interface UserInfo {
  username: string
  id: number
  email?: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface UserCreate {
  username: string
  password: string
}

export default {
  /**
   * 用户登录
   */
  async login(data: LoginData): Promise<LoginResponse> {
    try {
      // 将登录数据转换为表单格式
      const formData = new URLSearchParams()
      formData.append('username', data.username)
      formData.append('password', data.password)
      
      // 添加调试日志
      console.log('登录参数:', {
        username: data.username,
        password: '***'
      })
      
      // 发送登录请求
      const response = await request.post<LoginResponse>('/api/auth/login', formData)
      
      // 添加调试日志
      console.log('登录响应原始数据:', response)
      
      // 保存令牌到localStorage
      if (response && typeof response === 'object' && 'access_token' in response) {
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('token_type', response.token_type || 'bearer')
        return response as LoginResponse
      } else {
        throw new Error('登录响应格式不正确')
      }
    } catch (error) {
      console.error('登录请求失败:', error)
      throw error
    }
  },

  /**
   * 用户登出
   */
  async logout(): Promise<void> {
    // 清除本地存储的令牌
    localStorage.removeItem('token')
    localStorage.removeItem('token_type')
    
    // 服务端登出(如果需要)
    try {
      await request.post('/api/auth/logout')
    } catch (error) {
      console.error('登出错误:', error)
    }
  },

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<UserInfo> {
    try {
      const response = await request.get<UserInfo>('/api/auth/me')
      if (response && typeof response === 'object') {
        return response as UserInfo
      } else {
        throw new Error('获取用户信息响应格式不正确')
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  },

  // 用户注册
  async register(data: UserCreate) {
    try {
      return await request.post('/api/auth/register', data)
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    }
  }
}