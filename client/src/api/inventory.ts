import request from '../utils/request'
import type {
  InventoryAnalysisQuery,
  InventoryAnalysis,
  CategoryAnalysis
} from '../types/inventory'

export default {
  // 获取库存分析数据
  getAnalysis(params: InventoryAnalysisQuery) {
    return request.get<InventoryAnalysis>('/api/inventory/analysis', { params })
  },

  // 获取品类分析数据
  getCategoryAnalysis(params: InventoryAnalysisQuery) {
    return request.get<CategoryAnalysis[]>('/api/inventory/analysis/category', { params })
  },

  // 生成库存分析数据
  calculateAnalysis(date: string, type: string) {
    return request.post('/api/inventory/analysis/calculate', { date, type })
  }
} 