export type ProductType = '普货' | '纺织' | '混装'
export type ProductStatus = 'active' | 'inactive'
export type StockOperationType = '入库' | '出库' | '调整'

export interface ProductQuery {
  page: number
  pageSize: number
  keyword?: string
  type?: ProductType
  category?: string
  status?: ProductStatus
}

export interface ProductListResponse {
  items: Product[]
  total: number
}

export interface ProductBase {
  sku: string
  name: string
  chineseName?: string
  description?: string
  type: ProductType
  category: string
  price: number
  cost: number
  weight?: number
  alertThreshold?: number
  tags?: string[]
  status?: ProductStatus
}

export interface Product extends ProductBase {
  id: number
  stock: number
  created_at: string
  updated_at: string
}

export interface ProductCreateParams {
  sku: string
  name: string
  chineseName?: string
  type: ProductType
  price: number
  cost: number
  alertThreshold?: number
  status: ProductStatus
}

export type ProductUpdateParams = Partial<ProductCreateParams>

export interface BatchCreateProduct {
  products: ProductCreateParams[]
}

export interface BatchDeleteProduct {
  ids: number[]
}

export interface UpdateStockRequest {
  type: 'in' | 'out'
  quantity: number
  reason?: string
}

export interface ProductExportRequest {
  ids?: number[]
  keyword?: string
  type?: ProductType
  status?: ProductStatus
  fields: string[]
} 