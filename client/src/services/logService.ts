import { http } from '../utils/http';
import { OperationLog, ListResponse } from '../types/api';

export interface LogQuery {
  page?: number;
  pageSize?: number;
  module?: string;
  action?: string;
  username?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
}

export interface LogStatistics {
  moduleStats: Array<{ _id: string; count: number }>;
  actionStats: Array<{ _id: string; count: number }>;
  userStats: Array<{ _id: string; count: number }>;
}

const logService = {
  list: async (params: LogQuery): Promise<ListResponse<OperationLog>> => {
    const response = await http.get<ListResponse<OperationLog>>('/api/logs', { params });
    return response.data;
  },

  getStatistics: async (params: { startDate?: string; endDate?: string }): Promise<LogStatistics> => {
    const response = await http.get<LogStatistics>('/api/logs/statistics', { params });
    return response.data;
  },

  deleteOldLogs: async (days: number): Promise<{ deletedCount: number }> => {
    const response = await http.delete<{ deletedCount: number }>('/api/logs', { data: { days } });
    return response.data;
  }
};

export default logService; 