<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="main-area">
      <router-view />
    </main>
    <LoginModal v-if="userStore.showLogin" />
    <PreviewModal />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppSidebar from '@/components/AppSidebar.vue'
import LoginModal from '@/components/LoginModal.vue'
import PreviewModal from '@/components/PreviewModal.vue'
import { useUserStore } from '@/stores'

const userStore = useUserStore()
const router = useRouter()

onMounted(() => {
  const token = localStorage.getItem('token')
  if (!token) {
    userStore.showLogin = true
  } else {
    userStore.fetchProfile().catch(() => {
      // token 失效，显示登录弹窗
      userStore.showLogin = true
    })
  }
})

// 全局路由错误处理：未登录时显示弹窗而非阻止导航
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    userStore.showLogin = true
  }
  next()
})
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--color-bg-primary);
  overflow: hidden;
}

.main-area {
  flex: 1;
  min-width: 0;
  overflow: hidden auto;
}
</style>
