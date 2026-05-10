<template>
  <aside class="sidebar">
    <div class="sidebar-top">
      <div class="logo">
        <div class="logo-icon">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <defs>
              <linearGradient id="logoGrad" x1="0" y1="0" x2="28" y2="28">
                <stop offset="0%" stop-color="var(--accent)" />
                <stop offset="100%" stop-color="#a855f7" />
              </linearGradient>
            </defs>
            <path d="M14 2L24 8.5V19.5L14 26L4 19.5V8.5L14 2Z" fill="url(#logoGrad)" opacity="0.9" />
            <path d="M14 6L20 10V18L14 22L8 18V10L14 6Z" fill="white" opacity="0.15" />
          </svg>
        </div>
      </div>
    </div>

    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.key"
        :to="item.path"
        class="nav-item"
        :class="{ active: currentView === item.key }"
        :title="item.label"
      >
        <component :is="item.icon" class="nav-icon" :size="22" />
        <span class="nav-label">{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-bottom">
      <template v-if="userStore.isLoggedIn">
        <div class="user-info">
          <div class="user-avatar">
            <UserIcon :size="16" />
          </div>
          <span class="user-name">{{ userStore.user?.username }}</span>
        </div>
        <button class="logout-btn" @click="userStore.logout" title="登出">
          <LogOutIcon :size="16" />
          <span>登出</span>
        </button>
      </template>
      <template v-else>
        <button class="login-btn" @click="userStore.showLogin = true">
          <LogInIcon :size="16" />
          <span>登录</span>
        </button>
      </template>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Home, Clock, Image, User, LogOut, LogIn } from 'lucide-vue-next'
import { useUserStore } from '@/stores'
import type { ViewType } from '@/types'

const route = useRoute()
const userStore = useUserStore()

const currentView = computed<ViewType>(() => (route.meta.view as ViewType) || 'generate')

const navItems = [
  { key: 'generate' as ViewType, label: '生成', path: '/generate', icon: Home },
  { key: 'history' as ViewType, label: '历史', path: '/history', icon: Clock },
  { key: 'assets' as ViewType, label: '资产', path: '/assets', icon: Image },
]
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
  flex-shrink: 0;
}

.sidebar-top {
  margin-bottom: 32px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  padding: 0 10px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 0;
  border-radius: 10px;
  color: var(--text-muted);
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: var(--bg-hover);
  color: var(--text-secondary);
}

.nav-item.active {
  background-color: var(--accent);
  color: white;
}

.nav-label {
  font-size: 11px;
}

.sidebar-bottom {
  width: 100%;
  padding: 0 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px;
  color: var(--text-secondary);
  font-size: 12px;
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn,
.login-btn {
  width: 100%;
  padding: 8px;
  border-radius: 8px;
  border: none;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.logout-btn:hover,
.login-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>
