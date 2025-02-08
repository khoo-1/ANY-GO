// 利润分析查询参数
export interface ProfitAnalysisQuery {
  type: 'daily' | 'weekly' | 'monthly'
  startDate?: string
  endDate?: string
}

// 利润总览数据
export interface ProfitOverview {
  totalSales: number
  totalCost: number
  grossProfit: number
  netProfit: number
  grossProfitRate: number
  netProfitRate: number
}

// 利润趋势数据
export interface ProfitTrend {
  dates: string[]
  sales: number[]
  grossProfit: number[]
  netProfit: number[]
}

// 商品利润数据
export interface ProductProfit {
  productId: number
  productSku: string
  productName: string
  salesQuantity: number
  salesAmount: number
  unitCost: number
  totalCost: number
  shippingCost: number
  grossProfit: number
  netProfit: number
  grossProfitRate: number
  netProfitRate: number
}

// 品类利润数据
export interface CategoryProfit {
  category: string
  totalProducts: number
  totalOrders: number
  salesQuantity: number
  salesAmount: number
  productCost: number
  shippingCost: number
  operationCost: number
  grossProfit: number
  netProfit: number
  grossProfitRate: number
  netProfitRate: number
  averageOrderValue: number
  averageProfitPerOrder: number
}

// 利润分析数据
export interface ProfitAnalysis extends ProfitOverview {
  trend: ProfitTrend
}

// 商品利润分析结果
export interface ProductProfitAnalysis {
  topProducts: ProductProfit[]
  bottomProducts: ProductProfit[]
} 