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
      userStore.showLogin = true
    })
  }
})

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
