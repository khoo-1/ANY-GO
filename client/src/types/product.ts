export type ProductType = '普货' | '纺织' | '混装'
export type ProductStatus = 'active' | 'inactive'

export interface Product {
  id: number
  sku: string
  name: string
  chineseName: string
  description?: string
  category: string
  type: ProductType
  price: number
  cost: number
  stock: number
  alertThreshold: number
  supplier?: string
  images: string[]
  status: ProductStatus
  isAutoCreated: boolean
  needsCompletion: boolean
  createdAt: string
  updatedAt: string
}

export interface ProductQuery {
  page?: number
  pageSize?: number
  keyword?: string
  type?: ProductType
  category?: string
  status?: ProductStatus
  showAutoCreated?: boolean
  needsCompletion?: boolean
  minStock?: number
  maxStock?: number
}

export interface ProductListResponse {
  items: Product[]
  total: number
  page: number
  pageSize: number
}

export interface ProductCreateParams {
  sku: string
  name: string
  chineseName?: string
  description?: string
  category?: string
  type: ProductType
  price: number
  cost?: number
  alertThreshold?: number
  supplier?: string
  images?: string[]
}

export interface ProductUpdateParams {
  name?: string
  chineseName?: string
  description?: string
  category?: string
  type?: ProductType
  price?: number
  cost?: number
  stock?: number
  alertThreshold?: number
  supplier?: string
  images?: string[]
  status?: ProductStatus
  needsCompletion?: boolean
}

export interface BatchCreateProduct {
  products: ProductCreateParams[]
}

export interface BatchDeleteProduct {
  ids: number[]
}

export interface UpdateStockRequest {
  quantity: number
  type: '入库' | '出库' | '调整'
  reason?: string
}

export interface ProductExportRequest {
  keyword?: string
  type?: ProductType
  category?: string
  minPrice?: number
  maxPrice?: number
  inStock?: boolean
  fields?: string[]
} 