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
  userStore.fetchProfile()
})
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--bg-primary);
}

.main-area {
  flex: 1;
  overflow: hidden;
  position: relative;
}
</style>
