import request from '../utils/request'
import type {
  PackingList,
  PackingListQuery,
  PackingListCreateParams,
  PackingListUpdateParams,
  ImportResult,
  ExportRequest,
  StoreStatistics
} from '../types/packing'

export default {
  // 获取装箱单列表
  list(params: PackingListQuery) {
    return request.get<{
      items: PackingList[]
      total: number
      page: number
      pageSize: number
    }>('/api/packing-lists', { params })
  },

  // 获取单个装箱单详情
  get(id: number) {
    return request.get<PackingList>(`/api/packing-lists/${id}`)
  },

  // 创建装箱单
  create(data: PackingListCreateParams) {
    return request.post<PackingList>('/api/packing-lists', data)
  },

  // 更新装箱单
  update(id: number, data: PackingListUpdateParams) {
    return request.put<PackingList>(`/api/packing-lists/${id}`, data)
  },

  // 删除装箱单
  delete(id: number) {
    return request.delete(`/api/packing-lists/${id}`)
  },

  // 审批装箱单
  approve(id: number) {
    return request.post(`/api/packing-lists/${id}/approve`)
  },

  // 批量审批装箱单
  batchApprove(ids: number[]) {
    return request.post('/api/packing-lists/batch-approve', { ids })
  },

  // 导入装箱单
  import(formData: FormData) {
    return request.post<ImportResult>('/api/packing-lists/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 导出装箱单
  export(data: ExportRequest) {
    return request.post('/api/packing-lists/export', data, {
      responseType: 'blob'
    })
  },

  // 获取店铺统计数据
  getStoreStatistics(params?: {
    startDate?: string
    endDate?: string
  }) {
    return request.get<StoreStatistics[]>('/api/packing-lists/statistics/store', {
      params
    })
  }
} 