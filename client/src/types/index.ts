// 通用响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  code?: number;
}

// 分页参数类型
export interface PaginationParams {
  page: number;
  pageSize: number;
}

// 查询参数类型
export interface QueryParams extends Partial<PaginationParams> {
  sortField?: string;
  sortOrder?: 'ascend' | 'descend';
  [key: string]: any;
} 