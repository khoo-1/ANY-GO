import request from '../utils/request'
import type { Product } from '../types/product'

export interface SearchProductsParams {
  keyword?: string
  type?: string
  category?: string
  minPrice?: number
  maxPrice?: number
  inStock?: boolean
}

export interface SearchProductsResponse {
  items: Product[]
  total: number
}

/**
 * 搜索商品
 */
export const searchProducts = (params: SearchProductsParams) => {
  return request.get<SearchProductsResponse>('/products/search', { params })
}

/**
 * 获取商品详情
 */
export const getProduct = (id: number) => {
  return request.get<Product>(`/products/${id}`)
}

/**
 * 获取商品类型列表
 */
export const getProductTypes = () => {
  return request.get<string[]>('/products/types')
}

/**
 * 获取商品分类列表
 */
export const getProductCategories = () => {
  return request.get<string[]>('/products/categories')
} 