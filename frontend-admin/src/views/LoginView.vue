<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h1>AiMediaMaker</h1>
        <p>管理后台登录</p>
      </div>
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-field">
          <label>用户名</label>
          <input v-model="username" type="text" placeholder="请输入用户名" required />
        </div>
        <div class="form-field">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" required />
        </div>
        <button type="submit" class="login-btn" :disabled="loading">
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

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-page);
}

.login-card {
  background: var(--color-card);
  border: 1px solid var(--color-borderc);
  border-radius: 16px;
  padding: 40px;
  width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  font-size: 24px;
  margin-bottom: 8px;
}

.login-header p {
  color: var(--color-txts);
  font-size: 14px;
}

.form-field {
  margin-bottom: 16px;
}

.form-field label {
  display: block;
  font-size: 13px;
  color: var(--color-txts);
  margin-bottom: 6px;
}

.form-field input {
  width: 100%;
  padding: 10px 12px;
  background: var(--color-active);
  border: 1px solid var(--color-borderc);
  border-radius: 8px;
  color: var(--color-txtp);
  font-size: 14px;
  outline: none;
}

.form-field input:focus {
  border-color: var(--color-accent);
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: var(--color-accent);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.login-btn:hover {
  background: var(--color-accent-hover);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
