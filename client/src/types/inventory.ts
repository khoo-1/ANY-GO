// 库存分析查询参数
export interface InventoryAnalysisQuery {
  type: 'daily' | 'weekly' | 'monthly'
  startDate?: string
  endDate?: string
}

// 库存总览数据
export interface InventoryOverview {
  totalProducts: number
  totalQuantity: number
  totalValue: number
  turnoverRate: number
  turnoverDays: number
  averageInventory: number
  inventoryCost: number
}

// 库存健康度数据
export interface InventoryHealth {
  activeProducts: number
  inactiveProducts: number
  stockoutProducts: number
  overstockProducts: number
}

// 周转率趋势数据
export interface TurnoverTrend {
  dates: string[]
  rates: number[]
}

// 品类分析数据
export interface CategoryAnalysis {
  category: string
  totalProducts: number
  totalStock: number
  totalValue: number
  turnoverRate: number
  turnoverDays: number
  activeProducts: number
  inactiveProducts: number
  stockoutProducts: number
  overstockProducts: number
}

// 库存分析数据
export interface InventoryAnalysis extends InventoryOverview, InventoryHealth {
  turnoverTrend: TurnoverTrend
} 