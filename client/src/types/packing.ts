export interface BoxQuantity {
  boxNo: string
  quantity: number
  specs?: string
}

export interface Product {
  id: number
  sku: string
  name: string
  chineseName: string
  type: string
  category?: string
  cost: number
  price: number
  stock: number
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

export interface PackingList {
  id?: number
  code: string
  date: string
  storeName: string
  type: string
  totalBoxes: number
  totalPieces: number
  totalWeight: number
  totalVolume: number
  items: PackingListItem[]
  boxSpecs: BoxSpecs[]
  remarks?: string
  status: 'pending' | 'approved' | 'rejected'
  createdAt: string
  updatedAt: string
}

export interface PackingListQuery {
  page?: number
  pageSize?: number
  keyword?: string
  type?: string
  status?: string
  startDate?: string
  endDate?: string
}

export interface ImportResult {
  success: boolean
  message: string
  total: number
  created: number
  updated: number
  failed: number
  errors: string[]
}

export interface ExportRequest {
  ids: number[]
  includeBoxSpecs: boolean
  includeProductDetails: boolean
}

export interface StoreStatistics {
  storeName: string
  totalLists: number
  totalProducts: number
  totalPieces: number
  totalBoxes: number
  totalValue: number
} 