export type StockOperationType = '入库' | '出库' | '调整' | '盘点'
export type TransitStockStatus = 'in_transit' | 'arrived' | 'cancelled'
export type TransportType = 'sea' | 'air'

export interface StockTimeline {
  id: number
  productId: number
  productSku: string
  productName: string
  date: string
  openingStock: number
  closingStock: number
  inTransit: number
  inTransitDetails: Array<{
    packingListId: number
    quantity: number
    estimatedArrival: string
  }>
  incoming: number
  outgoing: number
  adjustments: number
}

export interface TransitStock {
  id: number
  productId: number
  productSku: string
  productName: string
  packingListId: number
  packingListNo: string
  quantity: number
  shippingDate: string
  estimatedArrival: string
  transportType: TransportType
  status: TransitStockStatus
  createdAt: string
  updatedAt: string
}

export interface StockTimelineQuery {
  page?: number
  pageSize?: number
  productId?: number
  startDate?: string
  endDate?: string
}

export interface TransitStockQuery {
  page?: number
  pageSize?: number
  productId?: number
  packingListId?: number
  transportType?: TransportType
  status?: TransitStockStatus
  startDate?: string
  endDate?: string
}

export interface TransitStockCreate {
  productId: number
  packingListId: number
  quantity: number
  shippingDate?: string
  estimatedArrival?: string
  transportType: TransportType
}

export interface TransitSummary {
  total: {
    quantity: number
    recordCount: number
  }
  byTransportType: {
    [key in TransportType]?: {
      quantity: number
      recordCount: number
    }
  }
} 