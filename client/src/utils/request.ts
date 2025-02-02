import axios, { AxiosError } from 'axios';
import { message } from 'antd';
import { ApiResponse } from '../types';

const request = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求重试配置
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

const retryRequest = async (error: AxiosError, retryCount: number = 0) => {
  const config = error.config;
  
  if (!config || retryCount >= MAX_RETRIES) {
    return Promise.reject(error);
  }

  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(axios(config));
    }, RETRY_DELAY * (retryCount + 1));
  });
};

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// 响应拦截器
request.interceptors.response.use(
  response => response.data,
  async (error: AxiosError<ApiResponse>) => {
    if (error.response) {
      // 服务器返回错误
      const errorMessage = error.response.data?.message || '请求失败，请稍后重试';
      message.error(errorMessage);
      
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    } else if (error.request) {
      // 请求发出但没有收到响应
      if (error.config) {
        try {
          const retryCount = (error.config as any).__retryCount || 0;
          (error.config as any).__retryCount = retryCount + 1;
          
          message.warning('正在重试连接...');
          return await retryRequest(error, retryCount);
        } catch (retryError) {
          message.error('网络连接失败，请检查网络设置或联系管理员');
        }
      }
    } else {
      // 请求配置出错
      message.error('请求配置错误，请联系管理员');
    }
    
    return Promise.reject(error);
  }
);

export default request; 