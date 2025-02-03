import { PaginationParams, QueryParams } from './index';

// 商品相关类型
export interface Product {
  id: string;
  sku: string;
  name: string;
  chineseName?: string;
  description?: string;
  category?: string;
  type: '普货' | '纺织' | '混装';
  price: number;
  cost?: number;
  stock: number;
  images?: string[];
  status: 'active' | 'inactive';
  isAutoCreated?: boolean;
  needsCompletion?: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ProductQuery extends QueryParams {
  keyword?: string;
  category?: string;
  type?: Product['type'];
  status?: Product['status'];
  minPrice?: number;
  maxPrice?: number;
}

export interface ProductCreate extends Omit<Product, 'id' | 'createdAt' | 'updatedAt'> {}
export interface ProductUpdate extends Partial<ProductCreate> {}

// 装箱单相关类型
export interface BoxSpecs {
  length: number;
  width: number;
  height: number;
  weight: number;
  volume: number;
  edgeVolume: number;
}

export interface BoxQuantity {
  boxNo: string;
  quantity: number;
  specs: BoxSpecs;
}

export interface PackingListItem {
  sku: string;
  chineseName?: string;
  boxQuantities: BoxQuantity[];
}

export interface PackingList {
  _id: string;
  storeName: string;
  type: string;
  totalBoxes: number;
  totalWeight: number;
  totalVolume: number;
  totalPieces: number;
  items: PackingListItem[];
  remarks?: string;
  createdAt: string;
  updatedAt: string;
}

export interface PackingListQuery {
  page?: number;
  pageSize?: number;
  storeName?: string;
  type?: string;
}

// 订单相关类型
export interface Order {
  id: string;
  orderNo: string;
  userId: string;
  products: Array<{
    productId: string;
    quantity: number;
    price: number;
  }>;
  totalAmount: number;
  status: 'pending' | 'paid' | 'shipped' | 'completed' | 'cancelled';
  createdAt: string;
  updatedAt: string;
}

export interface OrderQuery extends QueryParams {
  orderNo?: string;
  status?: Order['status'];
  startDate?: string;
  endDate?: string;
}

// 通用列表响应类型
export interface ListResponse<T> {
  items: T[];
  pagination: {
    total: number;
    current: number;
    pageSize: number;
  };
}

// API 响应类型
export interface ApiResponse<T = any> {
  message?: string;
  error?: string;
  data?: T;
} 