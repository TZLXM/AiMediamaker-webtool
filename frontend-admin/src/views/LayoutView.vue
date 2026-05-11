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
import { useAdminStore } from '@/stores'

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
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--border);
}

.sidebar-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.badge {
  display: inline-block;
  margin-top: 4px;
  padding: 2px 8px;
  background: var(--accent);
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
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--accent);
  color: white;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border);
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
  background: var(--bg-tertiary);
  border-radius: 4px;
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.logout-btn {
  width: 100%;
  padding: 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: var(--accent-danger);
  color: white;
  border-color: var(--accent-danger);
}

.main-content {
  flex: 1;
  overflow: auto;
  padding: 24px;
}
</style>
