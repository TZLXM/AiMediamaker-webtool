<template>
  <Teleport to="body">
    <Transition name="fade">
      <div class="login-overlay" @click.self="userStore.showLogin = false">
        <Transition name="scale-in">
          <div class="login-card">
            <div class="login-logo">
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <defs>
                  <linearGradient id="logoGradModal" x1="0" y1="0" x2="28" y2="28">
                    <stop offset="0%" stop-color="#6366f1" />
                    <stop offset="100%" stop-color="#8b5cf6" />
                  </linearGradient>
                </defs>
                <path d="M14 2L24 8.5V19.5L14 26L4 19.5V8.5L14 2Z" fill="url(#logoGradModal)" opacity="0.9" />
                <path d="M14 6L20 10V18L14 22L8 18V10L14 6Z" fill="white" opacity="0.15" />
              </svg>
            </div>
            <div class="login-header">
              <h2>账号登录</h2>
              <p>登录后即可使用AI图片视频生成</p>
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
              <button type="submit" class="login-submit" :disabled="loading">
                <span v-if="loading" class="spin">加载中...</span>
                <span v-else>登录</span>
              </button>
            </form>
            <p class="login-note">注意：平台暂不支持自主注册账号，请联系管理员分配账号</p>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores'

const userStore = useUserStore()
const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value.trim() || !password.value.trim()) return
  loading.value = true
  try {
    await userStore.login(username.value, password.value)
    username.value = ''
    password.value = ''
  } catch (e) {
    alert('登录失败：' + (e as Error).message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-overlay {
  position: fixed;
  inset: 0;
  background: #0a0a0feb;
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.login-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 12px 48px #00000080;
}

.login-logo {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.login-header h2 {
  font-size: 20px;
  margin-bottom: 8px;
  color: var(--color-text-primary);
}

.login-header p {
  color: var(--color-text-muted);
  font-size: 13px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-field input {
  width: 100%;
  height: 44px;
  padding: 0 14px;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  color: var(--color-text-primary);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-field input:focus {
  border-color: var(--color-accent);
}

.login-submit {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: filter 0.2s;
}

.login-submit:hover {
  filter: brightness(1.1);
}

.login-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-note {
  margin-top: 20px;
  font-size: 12px;
  color: var(--color-text-muted);
  text-align: center;
  line-height: 1.5;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-in-enter-active,
.scale-in-leave-active {
  transition: all 0.3s ease;
}
.scale-in-enter-from,
.scale-in-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
