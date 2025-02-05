import { http } from '../utils/http';
import { QueryParams, PagedResponse } from '../types/api';

// 利润分析相关的接口类型
interface ProfitAnalysis {
  id: number;
  date: string;
  type: 'daily' | 'weekly' | 'monthly';
  totalOrders: number;
  totalSales: number;
  productCost: number;
  shippingCost: number;
  operationCost: number;
  otherCost: number;
  totalCost: number;
  grossProfit: number;
  netProfit: number;
  grossProfitRate: number;
  netProfitRate: number;
}

interface ProductProfit {
  id: number;
  productId: number;
  productSku: string;
  productName: string;
  date: string;
  type: 'daily' | 'weekly' | 'monthly';
  salesQuantity: number;
  salesAmount: number;
  unitCost: number;
  totalCost: number;
  shippingCost: number;
  grossProfit: number;
  netProfit: number;
  grossProfitRate: number;
  netProfitRate: number;
}

interface CategoryProfit {
  id: number;
  category: string;
  date: string;
  type: 'daily' | 'weekly' | 'monthly';
  totalProducts: number;
  totalOrders: number;
  salesQuantity: number;
  salesAmount: number;
  productCost: number;
  shippingCost: number;
  operationCost: number;
  grossProfit: number;
  netProfit: number;
  grossProfitRate: number;
  netProfitRate: number;
  averageOrderValue: number;
  averageProfitPerOrder: number;
}

interface ProfitSummary {
  overallGrossProfit: number;
  overallNetProfit: number;
  overallGrossProfitRate: number;
  overallNetProfitRate: number;
  totalSales: number;
  totalCost: number;
  profitTrend: Array<{
    date: string;
    totalSales: number;
    grossProfit: number;
    netProfit: number;
    grossProfitRate: number;
    netProfitRate: number;
  }>;
  topProfitProducts: Array<{
    id: number;
    sku: string;
    name: string;
    salesAmount: number;
    netProfit: number;
    profitRate: number;
  }>;
  bottomProfitProducts: Array<{
    id: number;
    sku: string;
    name: string;
    salesAmount: number;
    netProfit: number;
    profitRate: number;
  }>;
  categoryAnalysis: Array<{
    category: string;
    salesAmount: number;
    netProfit: number;
    profitRate: number;
    avgOrderValue: number;
    avgProfitPerOrder: number;
  }>;
}

const profitService = {
  // 获取利润分析列表
  getAnalysisList: async (params: QueryParams): Promise<PagedResponse<ProfitAnalysis>> => {
    const response = await http.get('/api/profit/analysis', { params });
    return response.data;
  },

  // 计算利润分析
  calculateAnalysis: async (date: string, type: string) => {
    const response = await http.post('/api/profit/analysis/calculate', { date, type });
    return response.data;
  },

  // 获取商品利润列表
  getProductProfits: async (params: QueryParams): Promise<PagedResponse<ProductProfit>> => {
    const response = await http.get('/api/profit/products', { params });
    return response.data;
  },

  // 获取品类利润列表
  getCategoryProfits: async (params: QueryParams): Promise<PagedResponse<CategoryProfit>> => {
    const response = await http.get('/api/profit/categories', { params });
    return response.data;
  },

  // 获取利润汇总信息
  getProfitSummary: async (params: { startDate?: string; endDate?: string }): Promise<ProfitSummary> => {
    const response = await http.get('/api/profit/summary', { params });
    return response.data;
  }
};

export type {
  ProfitAnalysis,
  ProductProfit,
  CategoryProfit,
  ProfitSummary
};

export default profitService; 