import { PaginationParams, QueryParams } from './index';

// 商品相关类型
export interface Product {
  id: string;
  sku: string;
  chineseName: string;
  type: '普货' | '纺织' | '混装';
  category?: string;
  cost: number;
  freightCost: number;
  stock: number;
  alertThreshold: number;
  status: 'active' | 'inactive';
  description?: string;
  images?: string[];
  createdAt: string;
  updatedAt: string;
}

export interface ProductQuery {
  page?: number;
  pageSize?: number;
  keyword?: string;
  type?: string;
  minCost?: number;
  maxCost?: number;
}

export interface ProductCreate extends Omit<Product, 'id' | 'createdAt' | 'updatedAt'> {}
export interface ProductUpdate extends Partial<ProductCreate> {}

// 装箱单相关类型
export interface BoxQuantity {
  boxNo: string;
  quantity: number;
  specs?: {
    length?: number;
    width?: number;
    height?: number;
    weight?: number;
  };
}

export interface PackingItem {
  productId: string;
  sku: string;
  chineseName: string;
  quantities: number[];
  boxQuantities: BoxQuantity[];
}

export interface PackingList {
  _id: string;
  storeName: string;
  type: string;
  items: PackingItem[];
  totalBoxes: number;
  totalPieces: number;
  totalWeight: number;
  totalVolume: number;
  remarks?: string;
  createdAt: string;
  updatedAt: string;
}

export interface PackingListQuery {
  page?: number;
  pageSize?: number;
  keyword?: string;
  type?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
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

// 用户相关类型
export interface User {
  _id: string;
  username: string;
  role: 'admin' | 'manager' | 'operator';
  permissions: string[];
  status: 'active' | 'inactive';
  lastLoginAt?: string;
  createdAt: string;
  updatedAt: string;
}

// 操作日志相关类型
export interface OperationLog {
  _id: string;
  userId: string;
  username: string;
  module: 'products' | 'packingLists' | 'users' | 'system';
  action: 'create' | 'update' | 'delete' | 'read' | 'import' | 'export' | 'backup';
  description: string;
  details?: any;
  ip?: string;
  userAgent?: string;
  status: 'success' | 'failure';
  createdAt: string;
}

// 备份相关类型
export interface Backup {
  _id: string;
  filename: string;
  size: number;
  type: 'full' | 'products' | 'packingLists';
  status: 'pending' | 'completed' | 'failed';
  path: string;
  createdBy: {
    _id: string;
    username: string;
  };
  description?: string;
  error?: string;
  createdAt: string;
  completedAt?: string;
}

// 通用响应类型
export interface ListResponse<T> {
  items: T[];
  pagination: {
    total: number;
    current: number;
    pageSize: number;
  };
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
} 