<template>
  <div class="h-screen flex items-center justify-center bg-page">
    <div class="bg-card border border-borderc rounded-card p-10 w-[400px]">
      <div class="text-center mb-8">
        <h1 class="text-2xl mb-2 font-semibold">AiMediaMaker</h1>
        <p class="text-txts text-sm">管理后台登录</p>
      </div>
      <form class="flex flex-col" @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-[13px] text-txts mb-1.5">用户名</label>
          <input v-model="username" type="text" placeholder="请输入用户名" required
            class="w-full h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
        </div>
        <div class="mb-4">
          <label class="block text-[13px] text-txts mb-1.5">密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" required
            class="w-full h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
        </div>
        <button type="submit" class="w-full h-9 bg-accent border-none rounded-btn text-white text-sm font-medium cursor-pointer transition-colors duration-200 hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

const router = useRouter()
const adminStore = useAdminStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await adminStore.login(username.value, password.value)
    router.push('/')
  } catch (e: any) {
    alert('登录失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}
</script>
