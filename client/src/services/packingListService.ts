import { http } from '../utils/http';
import { PackingList, PackingListQuery, ListResponse, ApiResponse } from '../types/api';
import dayjs from 'dayjs';

// MongoDB ObjectId格式验证
const isValidObjectId = (id: string): boolean => {
  const objectIdPattern = /^[0-9a-fA-F]{24}$/;
  return objectIdPattern.test(id);
};

export const packingListService = {
  list: async (params: PackingListQuery = {}): Promise<ListResponse<PackingList>> => {
    console.log('调用list服务，参数:', params);
    try {
      const response = await http.get('/api/packing-lists', { params });
      console.log('list服务原始响应:', response);
      
      // 检查响应数据
      if (!response || !response.data) {
        console.error('服务器响应异常:', response);
        throw new Error('服务器响应异常');
      }

      const responseData = response.data;
      console.log('处理后的列表数据:', responseData);

      // 确保返回的数据符合 ListResponse 接口
      return {
        code: 0,
        items: Array.isArray(responseData.items) ? responseData.items : [],
        pagination: {
          total: responseData.pagination?.total || 0,
          current: params.page || 1,
          pageSize: params.pageSize || 10
        },
        message: '获取成功'
      };
    } catch (error) {
      console.error('list服务出错:', error);
      throw error;
    }
  },
  
  getById: async (id: string): Promise<PackingList> => {
    console.log('调用getById服务，ID:', id);
    const response = await http.get<ApiResponse<PackingList>>(`/api/packing-lists/${id}`);
    console.log('getById服务响应:', response);
    return response.data.data;
  },
  
  import: async (file: File): Promise<ApiResponse<any>> => {
    console.log('调用import服务，文件:', file.name);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await http.post<any>('/api/packing-lists/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 30000
      });
      console.log('import服务原始响应:', response);

      // 检查响应数据
      if (!response || !response.data) {
        console.error('服务器响应异常:', response);
        throw new Error('服务器响应异常');
      }

      const responseData = response.data;
      console.log('处理后的导入响应:', responseData);

      // 处理导入响应
      if (Array.isArray(responseData)) {
        return {
          code: 0,
          data: responseData,
          message: `成功导入 ${responseData.length} 个装箱单`
        };
      } else {
        return {
          code: 0,
          data: responseData,
          message: '导入成功'
        };
      }
    } catch (error) {
      console.error('import服务出错:', error);
      throw error;
    }
  },
  
  delete: async (id: string): Promise<void> => {
    console.log('调用delete服务，ID:', id);
    if (!id || typeof id !== 'string' || !isValidObjectId(id)) {
      console.error('无效的ID格式:', id);
      throw new Error('无效的ID格式，ID必须是24位的十六进制字符串');
    }
    const response = await http.delete<ApiResponse<void>>(`/api/packing-lists/${id}`);
    console.log('delete服务响应:', response);
  },
  
  deleteAll: async (): Promise<ApiResponse<void>> => {
    console.log('调用deleteAll服务');
    const response = await http.delete<ApiResponse<void>>('/api/packing-lists');
    console.log('deleteAll服务响应:', response);
    return response.data;
  },
  
  export: async (id: string): Promise<Blob> => {
    console.log('调用export服务，ID:', id);
    try {
      const response = await http.get<Blob>(`/api/packing-lists/${id}/download`, {
        responseType: 'blob'
      });
      const blob = response.data;
      console.log('export服务响应:', blob);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `装箱单_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      return blob;
    } catch (error) {
      console.error('export服务出错:', error);
      throw error;
    }
  },

  batchExport: async (ids: string[]): Promise<Blob> => {
    try {
      const response = await http.post<Blob>('/api/packing-lists/batch-download', { ids }, { responseType: 'blob' });
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `装箱单批量导出_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      return blob;
    } catch (error) {
      console.error('批量导出失败:', error);
      throw error;
    }
  }
}; 