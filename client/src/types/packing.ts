import type { Product } from './product'

export interface BoxQuantity {
  boxNo: string
  quantity: number
  specs?: string
}

export interface PackingListItem {
  id?: number
  productId: number
  product: Product
  quantity: number
  boxQuantities: BoxQuantity[]
  weight: number
  volume: number
}

export interface BoxSpecs {
  length: number
  width: number
  height: number
  weight: number
  volume: number
  edgeVolume: number
  totalPieces: number
}

export interface PackingItem {
  id: number
  productId: number
  product: Product
  quantity: number
  note?: string
}

export interface PackingList {
  id: number
  code: string
  status: '待审核' | '已审核' | '已取消'
  storeName?: string
  type?: string
  totalBoxes?: number
  totalPieces?: number
  totalValue?: number
  totalWeight?: number
  items: PackingItem[]
  createdAt: string
  updatedAt: string
}

export interface PackingListQuery {
  page: number
  pageSize: number
  keyword?: string
  status?: PackingList['status']
}

export interface PackingListResponse {
  items: PackingList[]
  total: number
}

export interface CreatePackingListParams {
  items: {
    productId: number
    quantity: number
    note?: string
  }[]
}

export type UpdatePackingListParams = Partial<CreatePackingListParams>

export interface PackingListExportRequest {
  ids?: number[]
  keyword?: string
  status?: PackingList['status']
  fields: string[]
}

export interface ImportResult {
  success: boolean
  message: string
  totalCount: number
  successCount: number
  failureCount: number
  errors?: string[]
}

export interface ExportRequest {
  ids: number[]
  includeBoxSpecs: boolean
  includeProductDetails: boolean
}

export interface StoreStatistics {
  storeId: number
  storeName: string
  totalOrders: number
  totalAmount: number
  averageAmount: number
  lastOrderDate: string
} 