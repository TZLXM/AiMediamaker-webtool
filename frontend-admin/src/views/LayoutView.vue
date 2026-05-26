<template>
  <div class="flex h-screen w-screen">
    <aside class="w-[var(--sidebar-width)] bg-card border-r border-borderc flex flex-col shrink-0">
      <div class="p-5 border-b border-borderc">
        <h2 class="text-lg font-semibold">AiMediaMaker</h2>
        <span class="inline-block mt-1 px-2 py-0.5 bg-accent text-white text-[11px] rounded">管理后台</span>
      </div>
      <nav class="flex-1 p-3 flex flex-col gap-1">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-2.5 px-3 py-2.5 rounded-btn text-sm transition-all duration-200 no-underline"
          :class="route.path === item.path ? 'bg-accent text-white' : 'text-txts hover:bg-hover hover:text-txtp'"
        >
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
      <div class="p-4 border-t border-borderc">
        <div class="flex items-center justify-between mb-3 text-[13px]">
          <span>{{ adminStore.user?.username }}</span>
          <span class="px-2 py-0.5 bg-active rounded text-[11px] text-txtm uppercase">{{ adminStore.user?.role }}</span>
        </div>
        <button class="w-full h-9 bg-active border border-borderc rounded-btn text-txts text-[13px] cursor-pointer flex items-center justify-center gap-1.5 transition-all duration-200 hover:bg-danger hover:text-white hover:border-danger" @click="handleLogout">
          <LogOutIcon :size="16" />
          <span>退出登录</span>
        </button>
      </div>
    </aside>
    <main class="flex-1 overflow-auto p-6">
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
