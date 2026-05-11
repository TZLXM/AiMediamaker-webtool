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
import AppSidebar from '@/components/AppSidebar.vue'
import LoginModal from '@/components/LoginModal.vue'
import PreviewModal from '@/components/PreviewModal.vue'
import { useUserStore } from '@/stores'

const userStore = useUserStore()

onMounted(() => {
  const token = localStorage.getItem('token')
  if (!token) {
    // 未登录，显示登录弹窗
    userStore.showLogin = true
  } else {
    userStore.fetchProfile()
  }
})
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--color-bg-primary);
}

.main-area {
  flex: 1;
  overflow: hidden;
  position: relative;
}
</style>
