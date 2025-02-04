import http from '../utils/http';
import { Backup, ListResponse } from '../types/api';

export interface BackupQuery {
  page?: number;
  pageSize?: number;
  type?: string;
  status?: string;
}

const backupService = {
  create: async (type: string): Promise<Backup> => {
    const response = await http.post<{ backup: Backup }>('/api/backups', { type });
    return response.data.backup;
  },

  list: async (params: BackupQuery): Promise<ListResponse<Backup>> => {
    const response = await http.get<ListResponse<Backup>>('/api/backups', { params });
    return response.data;
  },

  restore: async (id: string): Promise<void> => {
    await http.post(`/api/backups/${id}/restore`);
  },

  delete: async (id: string): Promise<void> => {
    await http.delete(`/api/backups/${id}`);
  }
};

export default backupService; 