import request from '../utils/request'
import type {
  StockTimeline,
  TransitStock,
  StockTimelineQuery,
  TransitStockQuery,
  TransitStockCreate,
  TransitSummary
} from '../types/stock'

export default {
  // 获取库存时间线
  getTimeline(params: StockTimelineQuery) {
    return request.get<StockTimeline[]>('/api/stock/timeline', { params })
  },

  // 生成库存时间线
  generateTimeline(startDate: string, endDate: string) {
    return request.post('/api/stock/timeline/generate', { startDate, endDate })
  },

  // 获取在途库存列表
  getTransitStock(params: TransitStockQuery) {
    return request.get<TransitStock[]>('/api/stock/transit', { params })
  },

  // 创建在途库存记录
  createTransitStock(data: TransitStockCreate) {
    return request.post<TransitStock>('/api/stock/transit', data)
  },

  // 更新在途库存状态
  updateTransitStatus(id: number, status: 'in_transit' | 'arrived' | 'cancelled') {
    return request.put(`/api/stock/transit/${id}/status`, { status })
  },

  // 获取在途库存汇总信息
  getTransitSummary(productId?: number) {
    return request.get<TransitSummary>('/api/stock/transit/summary', {
      params: { productId }
    })
  }
} 