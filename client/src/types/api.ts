import { PaginationParams, QueryParams } from './index';

// 商品相关类型
export interface Product {
  _id: string;
  id: string;
  sku: string;
  name: string;
  chineseName: string;
  type: '普货' | '纺织' | '混装';
  category?: string;
  cost: number;
  freightCost: number;
  stock: number;
  alertThreshold?: number;
  status: 'active' | 'inactive';
  description?: string;
  images?: string[];
  isAutoCreated: boolean;
  needsCompletion: boolean;
  createdAt: Date;
  updatedAt?: Date;
}

export interface ProductQuery extends QueryParams {
  keyword?: string;
  type?: '普货' | '纺织' | '混装';
  category?: string;
  status?: 'active' | 'inactive';
  showAutoCreated?: boolean;
  needsCompletion?: boolean;
}

export interface ProductCreate extends Omit<Product, '_id' | 'id' | 'createdAt' | 'updatedAt'> {}
export interface ProductUpdate extends Partial<ProductCreate> {}

// 装箱单相关类型
export interface BoxQuantity {
  boxNo: string;
  quantity: number;
  specs?: string;
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
  type: 'normal' | 'textile' | 'mixed';
  totalBoxes: number;
  totalWeight: number;
  totalVolume: number;
  totalValue: number;
  totalPieces: number;
  status: 'pending' | 'approved';
  items: PackingListItem[];
  remarks?: string;
  createdAt: Date;
  updatedAt?: Date;
  approvedAt?: Date;
  approvedBy?: string;
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
  lastLoginAt?: Date;
  createdAt: Date;
  updatedAt?: Date;
}

// 操作日志相关类型
export interface OperationLog {
  _id: string;
  userId: string;
  username: string;
  module: string;
  action: string;
  description: string;
  details: {
    method: string;
    url: string;
    body?: any;
    params?: any;
    query?: any;
  };
  ip: string;
  userAgent: string;
  status: 'success' | 'failure';
  createdAt: Date;
}

// 备份相关类型
export interface Backup {
  _id: string;
  filename: string;
  type: 'full' | 'products' | 'packingLists';
  size: number;
  path: string;
  status: 'pending' | 'completed' | 'failed';
  error?: string;
  createdBy: string;
  createdAt: Date;
  completedAt?: Date;
}

// 通用响应类型
export interface ApiResponse<T> {
  code?: number;
  data: T;
  message?: string;
}

// 列表响应类型
export interface ListResponse<T> {
  code?: number;
  items: T[];
  pagination: {
    total: number;
    current: number;
    pageSize: number;
  };
  message?: string;
}

// 装箱单明细类型
export interface PackingListItem {
  product: string | Product;
  boxQuantities: BoxQuantity[];
  totalQuantity: number;
  sku: string;
  chineseName: string;
}

// 查询参数类型
export interface BaseQuery {
  page?: number;
  pageSize?: number;
  keyword?: string;
}

export interface UserQuery extends BaseQuery {
  role?: string;
  status?: string;
}

export interface LogQuery extends BaseQuery {
  module?: string;
  action?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
}

export interface BackupQuery extends BaseQuery {
  type?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
} 