import request from '../utils/request'
import type {
  PackingList,
  PackingListQuery,
  ImportResult,
  ExportRequest,
  StoreStatistics
} from '../types/packing'

export function getPackingLists(params: PackingListQuery) {
  return request.get('/packing-lists', { params })
}

export function getPackingList(id: number) {
  return request.get(`/packing-lists/${id}`)
}

export function createPackingList(data: Partial<PackingList>) {
  return request.post('/packing-lists', data)
}

export function updatePackingList(id: number, data: Partial<PackingList>) {
  return request.put(`/packing-lists/${id}`, data)
}

export function deletePackingList(id: number) {
  return request.delete(`/packing-lists/${id}`)
}

export function getStoreStatistics(params?: {
  startDate?: string
  endDate?: string
}) {
  return request.get<StoreStatistics[]>('/packing-lists/statistics/store', {
    params
  })
}

export function approvePackingLists(ids: number[]) {
  return request.post('/packing-lists/batch-approve', {
    ids,
    action: 'approve'
  })
}

export function rejectPackingLists(ids: number[]) {
  return request.post('/packing-lists/batch-approve', {
    ids,
    action: 'reject'
  })
}

export interface ImportResult {
  success: boolean
  error?: string
  total?: number
  success_count?: number
  error_count?: number
  error_messages?: string[]
}

export interface ExportRequest {
  ids?: number[]
  start_date?: string
  end_date?: string
  include_box_specs?: boolean
}

/**
 * 导入装箱单
 */
export const importPackingLists = (data: FormData) => {
  return request.post<ImportResult>('/packing-lists/import', data, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出装箱单
 */
export const exportPackingLists = (data: ExportRequest) => {
  return request.post('/packing-lists/export', data, {
    responseType: 'blob'
  })
} 