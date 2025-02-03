import { Product, ProductCreate, ProductQuery } from '../types/api';
import { http } from '../utils/http';

export const productService = {
  getList: async (query: ProductQuery) => {
    const response = await http.get('/products', { params: query });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await http.get(`/products/${id}`);
    return response.data;
  },

  create: async (data: ProductCreate | FormData) => {
    const response = await http.post('/products', data, {
      headers: data instanceof FormData ? {
        'Content-Type': 'multipart/form-data'
      } : {
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  },

  update: async (id: string, data: Partial<ProductCreate> | FormData) => {
    const response = await http.put(`/products/${id}`, data, {
      headers: data instanceof FormData ? {
        'Content-Type': 'multipart/form-data'
      } : {
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  },

  delete: async (id: string) => {
    const response = await http.delete(`/products/${id}`);
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

  export: async (query: ProductQuery) => {
    const response = await http.get('/products/export', {
      params: query,
      responseType: 'blob'
    });
    return response.data;
  }
}; 