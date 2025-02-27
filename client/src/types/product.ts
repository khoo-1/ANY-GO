export type ProductType = '普货' | '纺织' | '混装'
export type StockOperationType = '入库' | '出库' | '调整'

export interface ProductQuery {
  page: number
  pageSize: number
  keyword?: string
  type?: ProductType
}

export interface ProductListResponse {
  items: Product[]
  total: number
}

export interface Product {
  id: number
  sku: string
  name: string
  type: ProductType
  price: number
  cost: number
  stock: number
  alertThreshold?: number
  createdAt: string
  updatedAt: string
}

export interface ProductCreateParams {
  sku: string
  name: string
  type: ProductType
  price: number
  cost: number
  alertThreshold?: number
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
  fields: string[]
} 