<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>AiMediaMaker</h2>
        <span class="badge">管理后台</span>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: route.path === item.path }"
        >
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="user-info">
          <span>{{ adminStore.user?.username }}</span>
          <span class="role">{{ adminStore.user?.role }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout">
          <LogOutIcon :size="16" />
          <span>退出登录</span>
        </button>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  LayoutDashboard,
  Box,
  Users,
  ListTodo,
  Settings,
  LogOut as LogOutIcon,
} from 'lucide-vue-next'
import { useAdminStore } from '@/stores/admin'

const route = useRoute()
const router = useRouter()
const adminStore = useAdminStore()

const menuItems = computed(() => [
  { path: '/dashboard', label: '系统状态', icon: LayoutDashboard },
  { path: '/models', label: '模型管理', icon: Box },
  { path: '/users', label: '用户管理', icon: Users },
  { path: '/tasks', label: '任务管理', icon: ListTodo },
  { path: '/system', label: '系统配置', icon: Settings },
])

function handleLogout() {
  adminStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.sidebar {
  width: var(--sidebar-width);
  background: var(--color-card);
  border-right: 1px solid var(--color-borderc);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--color-borderc);
}

.sidebar-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.badge {
  display: inline-block;
  margin-top: 4px;
  padding: 2px 8px;
  background: var(--color-accent);
  color: white;
  font-size: 11px;
  border-radius: 4px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  color: var(--color-txts);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--color-hover);
  color: var(--color-txtp);
}

.nav-item.active {
  background: var(--color-accent);
  color: white;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--color-borderc);
}

.user-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 13px;
}

.role {
  padding: 2px 8px;
  background: var(--color-active);
  border-radius: 4px;
  font-size: 11px;
  color: var(--color-txtm);
  text-transform: uppercase;
}

.logout-btn {
  width: 100%;
  padding: 8px;
  background: var(--color-active);
  border: 1px solid var(--color-borderc);
  border-radius: 6px;
  color: var(--color-txts);
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: var(--color-danger);
  color: white;
  border-color: var(--color-danger);
}

.main-content {
  flex: 1;
  overflow: auto;
  padding: 24px;
}
</style>
