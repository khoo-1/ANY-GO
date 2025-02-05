import axios, { AxiosRequestConfig, AxiosError } from 'axios';
import { message } from 'antd';
import { ApiResponse } from '../types';

// 设置后端服务地址
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';  // 修改为 5000 端口

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,  // 增加超时时间
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求重试配置
const MAX_RETRIES = 2;
const RETRY_DELAY = 500;

// 检查服务器是否可用
const checkServerAvailability = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/`, { timeout: 5000 });
    return response.status === 200;
  } catch (error) {
    console.error('服务器检查失败:', error);
    return false;
  }
};

const retryRequest = async (error: AxiosError, retryCount: number = 0) => {
  const config = error.config;
  
  if (!config || retryCount >= MAX_RETRIES) {
    message.error(`服务器连接失败 (${API_BASE_URL})，请检查后端服务是否正常运行`);
    return Promise.reject(error);
  }

  // 检查服务器是否可用
  const isServerAvailable = await checkServerAvailability();
  if (!isServerAvailable) {
    message.error(`后端服务未启动或端口(${API_BASE_URL})不正确，请检查服务器状态`);
    return Promise.reject(new Error('后端服务未启动'));
  }

  return new Promise((resolve) => {
    setTimeout(() => {
      message.warning(`第 ${retryCount + 1} 次重试连接...`);
      resolve(axios(config));
    }, RETRY_DELAY * (retryCount + 1));
  });
};

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.url, config.params || config.data);
    return config;
  },
  (error) => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.config.url, response.data);
    return response;
  },
  async (error) => {
    console.error('响应错误:', error);
    
    if (error.response) {
      const { status, data } = error.response;
      if (status === 404) {
        message.error('请求的资源不存在');
      } else if (status === 400) {
        message.error(data.message || '请求参数错误');
      } else if (status === 500) {
        message.error(data.message || '服务器内部错误');
      } else if (status === 401) {
        message.error('未授权访问');
      }
    } else if (error.request) {
      if (error.config) {
        const retryCount = (error.config as any).__retryCount || 0;
        (error.config as any).__retryCount = retryCount + 1;
        
        try {
          return await retryRequest(error, retryCount);
        } catch (retryError) {
          message.error(`请检查后端服务是否在 ${API_BASE_URL} 运行`);
        }
      }
    } else {
      message.error('请求配置错误，请检查网络设置');
    }
    return Promise.reject(error);
  }
);

export default request; 