import request from '../utils/request'

export interface UserLogin {
  username: string
  password: string
}

export interface UserCreate {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  token_type: string
}

export default {
  // 用户登录
  login(data: UserLogin) {
    const params = new URLSearchParams()
    params.append('username', data.username)
    params.append('password', data.password)
    
    // 添加调试日志
    console.log('登录参数:', { username: data.username, password: '***' })
    
    return request.post<LoginResponse>('/api/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },

  // 用户注册
  register(data: UserCreate) {
    return request.post('/api/auth/register', data)
  },

  // 退出登录
  logout() {
    return request.post('/api/auth/logout')
  }
}