import request from '../utils/request'
import type {
  ProfitAnalysisQuery,
  ProfitAnalysis,
  CategoryProfit,
  ProductProfitAnalysis
} from '../types/profit'

export default {
  // 获取利润分析数据
  getAnalysis(params: ProfitAnalysisQuery) {
    return request.get<ProfitAnalysis>('/api/profit/analysis', { params })
  },

  // 获取品类分析数据
  getCategoryAnalysis(params: ProfitAnalysisQuery) {
    return request.get<CategoryProfit[]>('/api/profit/analysis/category', { params })
  },

  // 获取商品分析数据
  getProductAnalysis(params: ProfitAnalysisQuery) {
    return request.get<ProductProfitAnalysis>('/api/profit/analysis/product', { params })
  },

  // 生成利润分析数据
  calculateAnalysis(date: string, type: string) {
    return request.post('/api/profit/analysis/calculate', { date, type })
  }
} 