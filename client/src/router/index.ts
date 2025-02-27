import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      {
        path: '',
        name: 'home',
        component: () => import('../views/Home.vue')
      },
      {
        path: 'products',
        name: 'products',
        component: () => import('../views/products/ProductList.vue'),
        meta: { title: '商品管理', icon: 'Goods' }
      },
      {
        path: 'packing-lists',
        name: 'packing-lists',
        component: () => import('../views/packing/PackingList.vue')
      },
      {
        path: 'packing-lists/create',
        name: 'packing-lists-create',
        component: () => import('../views/packing/PackingEdit.vue')
      },
      {
        path: 'packing-lists/:id',
        name: 'packing-lists-detail',
        component: () => import('../views/packing/PackingDetail.vue')
      },
      {
        path: 'packing-lists/:id/edit',
        name: 'packing-lists-edit',
        component: () => import('../views/packing/PackingEdit.vue')
      },
      {
        path: 'packing-lists/:id/print',
        name: 'packing-lists-print',
        component: () => import('../views/packing/PackingPrint.vue')
      },
      {
        path: 'profit',
        name: 'profit',
        component: () => import('../views/profit/ProfitAnalysis.vue')
      },
      {
        path: 'stock',
        name: 'stock',
        component: () => import('../views/stock/StockTimeline.vue'),
        meta: { title: '库存时间线', icon: 'Histogram', permission: 'stock:read' }
      },
      {
        path: 'stock/transit',
        name: 'transit-stock',
        component: () => import('../views/stock/TransitStock.vue'),
        meta: { title: '在途库存', icon: 'Ship', permission: 'stock:read' }
      },
      {
        path: 'stock/analysis',
        name: 'inventory-analysis',
        component: () => import('../views/inventory/InventoryAnalysis.vue'),
        meta: { title: '库存分析', icon: 'DataLine', permission: 'stock:read' }
      },
      {
        path: 'sales',
        name: 'sales',
        component: () => import('../views/sales/OrderList.vue'),
        meta: { title: '销售订单', icon: 'ShoppingCart', permission: 'sales:read' }
      }
    ]
  },
  {
    path: '/user',
    component: () => import('../views/Layout.vue'),
    redirect: '/user/list',
    meta: { title: '用户管理', icon: 'User', permission: 'users:read' },
    children: [
      {
        path: 'list',
        name: 'UserList',
        component: () => import('../views/user/UserList.vue'),
        meta: { title: '用户列表', permission: 'users:read' }
      }
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router 