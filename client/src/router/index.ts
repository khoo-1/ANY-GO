import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../views/Home.vue')
      },
      {
        path: 'products',
        name: 'products',
        component: () => import('../views/products/ProductList.vue')
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