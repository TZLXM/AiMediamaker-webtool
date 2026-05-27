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
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    redirect: '/generate',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    // 通过事件通知 App.vue 显示登录弹窗
    window.dispatchEvent(new CustomEvent('auth:required'))
  }
  next()
})

export default router
