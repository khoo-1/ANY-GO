import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页', icon: 'HomeFilled', requiresAuth: true }
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
        meta: { title: '商品管理', icon: 'Goods', requiresAuth: true }
      },
      {
        path: 'packing',
        name: 'packing',
        component: () => import('../views/packing/PackingList.vue'),
        meta: { title: '装箱单', icon: 'Document', requiresAuth: true }
      },
      {
        path: 'packing/create',
        name: 'packing-create',
        component: () => import('../views/packing/PackingEdit.vue')
      },
      {
        path: 'packing/:id',
        name: 'packing-detail',
        component: () => import('../views/packing/PackingDetail.vue')
      },
      {
        path: 'packing/:id/edit',
        name: 'packing-edit',
        component: () => import('../views/packing/PackingEdit.vue')
      },
      {
        path: 'packing/:id/print',
        name: 'packing-print',
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
        meta: { title: '库存时间线', icon: 'Histogram', permission: 'stock:read', requiresAuth: true }
      },
      {
        path: 'stock/transit',
        name: 'transit-stock',
        component: () => import('../views/stock/TransitStock.vue'),
        meta: { title: '在途库存', icon: 'Ship', permission: 'stock:read', requiresAuth: true }
      },
      {
        path: 'stock/analysis',
        name: 'inventory-analysis',
        component: () => import('../views/inventory/InventoryAnalysis.vue'),
        meta: { title: '库存分析', icon: 'DataLine', permission: 'stock:read', requiresAuth: true }
      },
      {
        path: 'sales',
        name: 'sales',
        component: () => import('../views/sales/OrderList.vue'),
        meta: { title: '销售订单', icon: 'ShoppingCart', permission: 'sales:read', requiresAuth: true }
      }
    ]
  },
  {
    path: '/user',
    component: () => import('../views/Layout.vue'),
    redirect: '/user/list',
    meta: { title: '用户管理', icon: 'User', permission: 'users:read', requiresAuth: true },
    children: [
      {
        path: 'list',
        name: 'UserList',
        component: () => import('../views/user/UserList.vue'),
        meta: { title: '用户列表', permission: 'users:read', requiresAuth: true }
      }
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 如果是从登录页面跳转来的，直接放行
  if (from.path === '/login' && userStore.isLoggedIn) {
    return next()
  }
  
  // 如果路由需要认证
  if (to.meta.requiresAuth) {
    try {
      // 检查认证状态
      const isAuthenticated = await userStore.checkAuth()
      
      if (isAuthenticated) {
        next()
      } else {
        next('/login')
      }
    } catch (error) {
      console.error('认证检查失败:', error)
      next('/login')
    }
  } else {
    // 如果已登录且访问登录页，重定向到首页
    if (to.path === '/login' && userStore.isLoggedIn) {
      next('/')
    } else {
      next()
    }
  }
})

export default router 