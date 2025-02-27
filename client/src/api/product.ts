import request from '../utils/request'
import type {
  Product,
  ProductQuery,
  ProductListResponse,
  ProductCreateParams,
  ProductUpdateParams,
  BatchCreateProduct,
  BatchDeleteProduct,
  UpdateStockRequest,
  ProductExportRequest
} from '../types/product'

export default {
  // 获取商品列表
  list(params: ProductQuery) {
    return request.get<ProductListResponse>('/api/products', { params })
  },

  // 获取单个商品详情
  get(id: number) {
    return request.get<Product>(`/api/products/${id}`)
  },

  // 创建商品
  create(data: ProductCreateParams) {
    return request.post<Product>('/api/products', data)
  },

  // 批量创建商品
  batchCreate(data: BatchCreateProduct) {
    return request.post<Product[]>('/api/products/batch', data)
  },

  // 更新商品
  update(id: number, data: ProductUpdateParams) {
    return request.put<Product>(`/api/products/${id}`, data)
  },

  // 删除商品
  delete(id: number) {
    return request.delete(`/api/products/${id}`)
  },

  // 批量删除商品
  batchDelete(data: BatchDeleteProduct) {
    return request.post('/api/products/batch-delete', data)
  },

  // 更新库存
  updateStock(id: number, data: UpdateStockRequest) {
    return request.post(`/api/products/${id}/stock`, data)
  },

  // 导出商品数据
  export(params: ProductExportRequest) {
    return request.get('/api/products/export', {
      params,
      responseType: 'blob'
    })
  },

  // 上传商品图片
  uploadImage(file: File) {
    const formData = new FormData()
    formData.append('image', file)
    return request.post<{ url: string }>('/api/products/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取商品类别列表
  getCategories(params?: { type?: string }) {
    return request.get<string[]>('/api/products/categories', { params })
  }
} 