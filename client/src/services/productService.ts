import request from '../utils/request';
import { Product, ProductQuery, ProductCreate, ProductUpdate, ListResponse } from '../types/api';

export const productService = {
  list: async (params: ProductQuery) => {
    return request.get<ListResponse<Product>>('/api/products', { params });
  },
  
  getById: async (id: string) => {
    return request.get<Product>(`/api/products/${id}`);
  },
  
  create: async (data: ProductCreate) => {
    return request.post<Product>('/api/products', data);
  },
  
  update: async (id: string, data: ProductUpdate) => {
    return request.put<Product>(`/api/products/${id}`, data);
  },
  
  delete: async (id: string) => {
    return request.delete(`/api/products/${id}`);
  },
  
  uploadImage: async (file: File) => {
    const formData = new FormData();
    formData.append('image', file);
    return request.post<string>('/api/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  importProducts: async (formData: FormData) => {
    return request.post<{ message: string; count: number }>('/api/products/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
}; 