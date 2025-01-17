export interface Product {
  _id: string;
  sku: string;
  name: string;
  description?: string;
  category?: string;
  price: number;
  cost?: number;
  stock: number;
  alertThreshold?: number;
  supplier?: string;
  images?: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface StockRecord {
  _id: string;
  product: Product | string;
  type: '入库' | '出库' | '调整';
  quantity: number;
  previousStock: number;
  currentStock: number;
  reason?: string;
  operator: string;
  date: Date;
} 