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
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
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
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 移除pending中的请求
    removePending(response.config)

    const { data } = response
    
    // 缓存GET请求的响应
    if (response.config.method?.toLowerCase() === 'get') {
      const cacheKey = generateKey(response.config)
      cache.set(cacheKey, data)
    }

    if (data.code === 0) {
      return data.data
    } else {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
  },
  (error) => {
    // 如果是缓存数据,直接返回
    if (error.response?.status === 200) {
      return error.response.data
    }

    // 移除pending中的请求
    error.config && removePending(error.config)

    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.response.data.message || '请求失败')
      }
    } else if (error.code === 'ERR_CANCELED') {
      // 请求被取消,不显示错误
      return
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default request 