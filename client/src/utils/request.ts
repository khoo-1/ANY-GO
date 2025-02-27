import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import { cache } from './cache'

// 防抖Map
const pendingMap = new Map<string, AbortController>()

// 生成请求Key
const generateKey = (config: AxiosRequestConfig) => {
  const { method, url, params, data } = config
  return [method, url, JSON.stringify(params), JSON.stringify(data)].join('&')
}

// 添加请求到pendingMap
const addPending = (config: AxiosRequestConfig) => {
  const key = generateKey(config)
  if (pendingMap.has(key)) {
    pendingMap.get(key)?.abort()
    pendingMap.delete(key)
  }
  const controller = new AbortController()
  config.signal = controller.signal
  pendingMap.set(key, controller)
}

// 从pendingMap中移除请求
const removePending = (config: AxiosRequestConfig) => {
  const key = generateKey(config)
  if (pendingMap.has(key)) {
    pendingMap.delete(key)
  }
}

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,  // 增加超时时间到30秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    console.log(`发送请求: ${config.url} ${config.method}`)
    
    // 对于登录请求，确保使用正确的Content-Type
    if (config.url === '/api/auth/login' && config.method === 'post') {
      config.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    }
    
    // 添加token到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 检查缓存
    if (config.method?.toLowerCase() === 'get') {
      const cacheKey = generateKey(config)
      const cachedData = cache.get(cacheKey)
      if (cachedData) {
        // 返回缓存数据
        return Promise.reject({
          config,
          response: {
            data: cachedData,
            status: 200,
            statusText: 'OK',
            headers: {},
            config
          }
        })
      }
    }

    // 防抖处理
    if (config.method?.toLowerCase() === 'get') {
      addPending(config)
    }

    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 添加调试日志
    console.log('收到响应:', response.status, response.data)
    
    // 移除pending中的请求
    removePending(response.config)

    // 直接返回响应数据，不再检查code
    return response.data
  },
  (error) => {
    console.error('响应错误:', error)
    
    if (error.response) {
      console.error('错误状态:', error.response.status)
      console.error('错误数据:', error.response.data)
      
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        router.push('/login')
      }
      
      ElMessage.error(
        error.response.data?.detail || 
        error.response.data?.message || 
        '请求失败'
      )
    } else if (error.request) {
      console.error('请求未收到响应:', error.request)
      ElMessage.error('服务器未响应，请检查网络连接')
    } else {
      console.error('请求配置错误:', error.message)
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default request 