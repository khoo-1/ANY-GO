import request from '../utils/request';
import { PackingList, PackingListQuery, ListResponse } from '../types/api';

export const packingListService = {
  list: async (params: PackingListQuery) => {
    return request.get<ListResponse<PackingList>>('/api/packing-lists', { params });
  },
  
  getById: async (id: string) => {
    return request.get<PackingList>(`/api/packing-lists/${id}`);
  },
  
  import: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request.post<{ message: string; data: PackingList[] }>('/api/packing-lists/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  updateStatus: async (id: string, status: PackingList['status']) => {
    return request.patch<PackingList>(`/api/packing-lists/${id}/status`, { status });
  },
  
  delete: async (id: string) => {
    return request.delete(`/api/packing-lists/${id}`);
  }
}; 