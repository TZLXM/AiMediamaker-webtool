import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import GenerateView from '@/views/GenerateView.vue'
import HistoryView from '@/views/HistoryView.vue'
import AssetsView from '@/views/AssetsView.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/generate' },
  {
    path: '/generate',
    name: 'generate',
    component: GenerateView,
    meta: { view: 'generate', requiresAuth: true },
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryView,
    meta: { view: 'history', requiresAuth: true },
  },
  {
    path: '/assets',
    name: 'assets',
    component: AssetsView,
    meta: { view: 'assets', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  // pinia 默认不持久化到 localStorage，直接读取 token
  const token = localStorage.getItem('token')
  const isLoggedIn = !!token

  if (to.meta.requiresAuth && !isLoggedIn) {
    // 取消导航，避免无限重定向（因为 / 会 redirect 回 /generate）
    next(false)
  } else {
    next()
  }
})

export default router
