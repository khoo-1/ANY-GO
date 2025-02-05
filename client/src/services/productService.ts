import { http } from '../utils/http';
import { Product, QueryParams, PagedResponse } from '../types/api';

const productService = {
  getList: async (params: QueryParams): Promise<PagedResponse<Product>> => {
    const response = await http.get<PagedResponse<Product>>('/api/products', { params });
    return response.data;
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