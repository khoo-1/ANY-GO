import request from '../utils/request'

export interface UserLogin {
  username: string
  password: string
}

export interface UserCreate {
  username: string
  password: string
}

export default {
  // 用户登录
  login(data: UserLogin) {
    const params = new URLSearchParams()
    params.append('username', data.username)
    params.append('password', data.password)
    return request.post<{ token: string }>('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },

  // 用户注册
  register(data: UserCreate) {
    return request.post('/auth/register', data)
  },

  // 退出登录
  logout() {
    return request.post('/auth/logout')
  }
}