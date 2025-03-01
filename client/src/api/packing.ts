import request from '@/utils/request'
import type {
  PackingList,
  PackingListQuery,
  PackingListResponse,
  CreatePackingListParams,
  UpdatePackingListParams,
  PackingListExportRequest,
  ImportResult,
  StoreStatistics
} from '@/types/packing'

const baseUrl = '/api/packing'

export default {
  // 获取打包清单列表
  list(params: PackingListQuery): Promise<PackingListResponse> {
    // 转换参数名称
    const queryParams = {
      page: params.page,
      page_size: params.pageSize,
      keyword: params.keyword,
      status: params.status
    }
    return request.get(baseUrl, { params: queryParams })
  },

  // 获取打包清单详情
  get(id: number): Promise<PackingList> {
    return request.get(`${baseUrl}/${id}`)
  },

  // 创建打包清单
  create(data: CreatePackingListParams): Promise<PackingList> {
    return request.post(baseUrl, data)
  },

  // 更新打包清单
  update(id: number, data: UpdatePackingListParams): Promise<PackingList> {
    return request.put(`${baseUrl}/${id}`, data)
  },

  // 删除打包清单
  delete(id: number): Promise<void> {
    return request.delete(`${baseUrl}/${id}`)
  },

  // 审批装箱单
  approve(id: number) {
    return request.post(`${baseUrl}/${id}/approve`)
  },

  // 批量审批装箱单
  batchApprove(ids: number[]) {
    return request.post(`${baseUrl}/batch-approve`, { ids })
  },

  // 导入装箱单
  import(formData: FormData) {
    return request.post<ImportResult>(`${baseUrl}/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 导出打包清单
  export(params: PackingListExportRequest): Promise<Blob> {
    return request.get(`${baseUrl}/export`, {
      params,
      responseType: 'blob'
    })
  },

  // 获取店铺统计数据
  getStoreStatistics(params?: {
    startDate?: string
    endDate?: string
  }) {
    return request.get<StoreStatistics[]>(`${baseUrl}/statistics/store`, {
      params
    })
  }
} 