<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="main-area">
      <router-view v-slot="{ Component }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>
    <LoginModal v-if="userStore.showLogin" />
    <PreviewModal />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import LoginModal from '@/components/LoginModal.vue'
import PreviewModal from '@/components/PreviewModal.vue'
import { useUserStore } from '@/stores'

const userStore = useUserStore()

function handleUnauthorized() {
  userStore.logout()
  userStore.showLogin = true
}

function handleAuthRequired() {
  userStore.showLogin = true
}

onMounted(() => {
  const token = localStorage.getItem('token')
  if (!token) {
    userStore.showLogin = true
  } else {
    userStore.fetchProfile().catch(() => {
      userStore.showLogin = true
    })
  }

  window.addEventListener('api:unauthorized', handleUnauthorized)
  window.addEventListener('auth:required', handleAuthRequired)
})

onUnmounted(() => {
  window.removeEventListener('api:unauthorized', handleUnauthorized)
  window.removeEventListener('auth:required', handleAuthRequired)
})
</script>

<style scoped>
.app-layout {
  display: flex;
  width: 100%;
  height: 100vh;
  background-color: var(--color-bg-primary);
  overflow: hidden;
}

.main-area {
  flex: 1;
  min-width: 0;
  overflow: hidden auto;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}
.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}
</style>
