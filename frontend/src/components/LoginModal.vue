<template>
  <Teleport to="body">
    <Transition name="fade">
      <div class="login-overlay" @click.self="userStore.showLogin = false">
        <Transition name="scale-in">
          <div class="login-card">
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
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.login-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 32px;
  width: 380px;
  max-width: 90vw;
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.login-header h2 {
  font-size: 20px;
  margin-bottom: 8px;
}

.login-header p {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.form-field {
  margin-bottom: 16px;
}

.form-field label {
  display: block;
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.form-field input {
  width: 100%;
  padding: 10px 12px;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-primary);
  font-size: 14px;
  outline: none;
}

.form-field input:focus {
  border-color: var(--color-accent);
}

.login-submit {
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

.login-submit:hover {
  background: var(--color-accent-hover);
}

.login-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-note {
  margin-top: 16px;
  font-size: 12px;
  color: var(--color-text-muted);
  text-align: center;
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
