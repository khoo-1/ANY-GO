import request from '../utils/request'
import type { Order } from '../types/sales'

export default {
  // 获取订单列表
  list(params: {
    page?: number
    pageSize?: number
    keyword?: string
    storeName?: string
    platform?: string
    status?: string
    paymentStatus?: string
    startDate?: string
    endDate?: string
    operatorId?: number
  }) {
    return request.get<{
      items: Order[]
      total: number
      page: number
      pageSize: number
    }>('/api/sales/orders', { params })
  },

  // 获取订单详情
  get(id: number) {
    return request.get<Order>(`/api/sales/orders/${id}`)
  },

  // 创建订单
  create(data: any) {
    return request.post<Order>('/api/sales/orders', data)
  },

  // 更新订单
  update(id: number, data: any) {
    return request.put<Order>(`/api/sales/orders/${id}`, data)
  },

  // 删除订单
  delete(id: number) {
    return request.delete(`/api/sales/orders/${id}`)
  },

  // 导出订单
  export(params: {
    keyword?: string
    storeName?: string
    platform?: string
    status?: string
    paymentStatus?: string
    startDate?: string
    endDate?: string
  }) {
    return request.post('/api/sales/orders/export', params, {
      responseType: 'blob'
    })
  },

  // 获取销售统计
  getStatistics(params: {
    startDate?: string
    endDate?: string
    storeName?: string
    platform?: string
  }) {
    return request.get('/api/sales/statistics', { params })
  },

  // 获取销售汇总
  getSummary(params: {
    startDate?: string
    endDate?: string
    storeName?: string
    platform?: string
  }) {
    return request.get('/api/sales/summary', { params })
  }
} 