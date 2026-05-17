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

export default router
