import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Product, PackingList } from '@/types/packing'

export const usePackingStore = defineStore('packing', () => {
  // 缓存的商品列表
  const cachedProducts = ref<Product[]>([])
  // 最近使用的装箱单模板
  const recentTemplates = ref<PackingList[]>([])
  // 导入历史
  const importHistory = ref<{
    filename: string
    timestamp: number
    success: boolean
    errors?: string[]
  }[]>([])
  // 性能指标
  const performanceMetrics = ref<{
    loadTime: number
    saveTime: number
    importTime: number
    searchTime: number
  }>({
    loadTime: 0,
    saveTime: 0,
    importTime: 0,
    searchTime: 0
  })

  // 缓存商品数据
  function cacheProducts(products: Product[]) {
    cachedProducts.value = products
  }

  // 添加模板
  function addTemplate(template: PackingList) {
    const maxTemplates = 5
    recentTemplates.value.unshift(template)
    if (recentTemplates.value.length > maxTemplates) {
      recentTemplates.value.pop()
    }
    // 保存到localStorage
    localStorage.setItem('packing_templates', JSON.stringify(recentTemplates.value))
  }

  // 记录导入历史
  function addImportHistory(history: {
    filename: string
    success: boolean
    errors?: string[]
  }) {
    importHistory.value.unshift({
      ...history,
      timestamp: Date.now()
    })
    if (importHistory.value.length > 10) {
      importHistory.value.pop()
    }
    // 保存到localStorage
    localStorage.setItem('packing_import_history', JSON.stringify(importHistory.value))
  }

  // 记录性能指标
  function recordPerformance(metric: keyof typeof performanceMetrics.value, time: number) {
    performanceMetrics.value[metric] = time
  }

  // 初始化store
  function initStore() {
    // 从localStorage加载数据
    const templates = localStorage.getItem('packing_templates')
    if (templates) {
      recentTemplates.value = JSON.parse(templates)
    }

    const history = localStorage.getItem('packing_import_history')
    if (history) {
      importHistory.value = JSON.parse(history)
    }
  }

  return {
    cachedProducts,
    recentTemplates,
    importHistory,
    performanceMetrics,
    cacheProducts,
    addTemplate,
    addImportHistory,
    recordPerformance,
    initStore
  }
}) 