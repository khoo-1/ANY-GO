// 利润分析路由
{
  path: '/profit',
  name: 'profit',
  meta: {
    title: '利润分析',
    icon: 'LineChartOutlined',
    permission: 'profit:read'
  },
  children: [
    {
      path: '/profit/analysis',
      name: 'profitAnalysis',
      component: () => import('../pages/profit/ProfitAnalysis'),
      meta: {
        title: '利润概览',
        permission: 'profit:read'
      }
    },
    {
      path: '/profit/products',
      name: 'productProfit',
      component: () => import('../pages/profit/ProductProfit'),
      meta: {
        title: '商品利润',
        permission: 'profit:read'
      }
    },
    {
      path: '/profit/categories',
      name: 'categoryProfit',
      component: () => import('../pages/profit/CategoryProfit'),
      meta: {
        title: '品类利润',
        permission: 'profit:read'
      }
    }
  ]
} 