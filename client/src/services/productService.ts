import { http } from '../utils/http';
import { Product, QueryParams, PagedResponse } from '../types/api';

const productService = {
  getList: async (params: QueryParams): Promise<PagedResponse<Product>> => {
    const queryParams = {
      ...params
    };
    console.log('发送请求到服务器，参数:', queryParams);
    const response = await http.get<{ code: number; data: PagedResponse<Product>; message: string }>('/api/products', { params: queryParams });
    console.log('服务器响应:', response.data);
    
    if (!response.data || !response.data.data) {
      console.error('服务器返回数据格式错误:', response.data);
      throw new Error('服务器返回数据格式错误');
    }

    const { items, total, page, pageSize } = response.data.data;
    return {
      items: items || [],
      total: total || 0,
      page: page || 1,
      pageSize: pageSize || 10
    };
  },

  getById: async (id: string): Promise<Product> => {
    const response = await http.get<Product>(`/api/products/${id}`);
    return response.data;
  },

  create: async (data: Partial<Product>): Promise<Product> => {
    const response = await http.post<Product>('/api/products', data);
    return response.data;
  },

  update: async (id: string, data: Partial<Product>): Promise<Product> => {
    const response = await http.put<Product>(`/api/products/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await http.delete(`/api/products/${id}`);
  },

  updateStatus: async (id: string, status: 'active' | 'inactive'): Promise<Product> => {
    const response = await http.patch<Product>(`/api/products/${id}/status`, { status });
    return response.data;
  },

  downloadTemplate: async () => {
    const response = await http.get('/products/template', {
      responseType: 'blob'
    });
    return response.data;
  },

  import: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await http.post('/products/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  export: async (query: QueryParams) => {
    const response = await http.get('/products/export', {
      params: query,
      responseType: 'blob'
    });
    return response.data;
  }
};

export default productService; 