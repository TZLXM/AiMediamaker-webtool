import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAdminStore } from '@/stores'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    name: 'layout',
    component: () => import('@/views/LayoutView.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '系统状态', icon: 'LayoutDashboard' },
      },
      {
        path: 'models',
        name: 'models',
        component: () => import('@/views/model/ModelListView.vue'),
        meta: { title: '模型管理', icon: 'Box' },
      },
      {
        path: 'models/edit/:id',
        name: 'model-edit',
        component: () => import('@/views/model/ModelEditView.vue'),
        meta: { title: '编辑模型', hidden: true },
      },
      {
        path: 'models/create',
        name: 'model-create',
        component: () => import('@/views/model/ModelEditView.vue'),
        meta: { title: '新增模型', hidden: true },
      },
      {
        path: 'users',
        name: 'users',
        component: () => import('@/views/user/UserListView.vue'),
        meta: { title: '用户管理', icon: 'Users' },
      },
      {
        path: 'tasks',
        name: 'tasks',
        component: () => import('@/views/task/TaskListView.vue'),
        meta: { title: '任务管理', icon: 'ListTodo' },
      },
      {
        path: 'system',
        name: 'system',
        component: () => import('@/views/system/SystemConfigView.vue'),
        meta: { title: '系统配置', icon: 'Settings' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const adminStore = useAdminStore()
  // 未登录且访问非公开页面 → 登录页
  if (!to.meta.public && !adminStore.isLoggedIn) {
    next('/login')
    return
  }
  // 已登录但非 admin 角色 → 无权限（退出到登录页）
  if (!to.meta.public && adminStore.user?.role !== 'admin') {
    adminStore.logout()
    next('/login')
    return
  }
  next()
})

export default router
