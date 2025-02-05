import { PaginationParams } from './index';

// 基础类型
export interface BaseModel {
  _id: string;
  id?: string;
  createdAt: string;
  updatedAt: string;
}

// 分页查询参数
export interface QueryParams {
  page: number;
  pageSize: number;
  keyword?: string;
  status?: string;
  type?: string;
  [key: string]: any;
}

// 状态类型
export type PackingListStatus = 'draft' | 'confirmed' | 'cancelled';

// 分页响应类型
export interface PagedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

// 用户相关类型
export interface User extends BaseModel {
  username: string;
  role: 'admin' | 'manager' | 'operator';
  permissions: string[];
  status: 'active' | 'inactive';
}

// 商品相关类型
export interface Product extends BaseModel {
  name: string;
  chineseName: string;
  sku: string;
  type: string;
  category?: string;
  description?: string;
  cost: number;
  freightCost: number;
  price: number;
  stock: number;
  alertThreshold: number;
  status: 'active' | 'inactive';
  images?: string[];
  isAutoCreated?: boolean;
  needsCompletion?: boolean;
}

// 箱子数量类型
export interface BoxQuantity {
  boxNo: string;
  quantity: number;
  specs?: string;
}

// 装箱单相关类型
export interface PackingList extends Omit<BaseModel, 'createdAt' | 'updatedAt'> {
  code: string;
  date: string;
  storeName: string;
  type: string;
  totalBoxes: number;
  totalPieces: number;
  totalWeight: number;
  totalVolume: number;
  items: PackingListItem[];
  remarks?: string;
  status: PackingListStatus;
  createdAt: string;
  updatedAt: string;
}

// 装箱单明细类型
export interface PackingListItem {
  sku: string;
  quantity: number;
  product: Product;
  boxQuantities: BoxQuantity[];
  weight: number;
  volume: number;
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number;
  data: T;
  message: string;
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
export interface PackingItem {
  productId: string;
  sku: string;
  chineseName: string;
  quantities: number[];
  boxQuantities: BoxQuantity[];
}

export interface PackingListQuery extends QueryParams {
  status?: PackingListStatus;
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

// 列表响应类型
export interface ListResponse<T> extends ApiResponse {
  items: T[];
  pagination: {
    total: number;
    current: number;
    pageSize: number;
  };
}

export interface UserQuery extends QueryParams {
  role?: string;
  status?: string;
}

export interface LogQuery extends QueryParams {
  module?: string;
  action?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
}

export interface BackupQuery extends QueryParams {
  type?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
} 