import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAdminStore = defineStore('admin', () => {
  const token = ref<string>(localStorage.getItem('admin_token') || '')
  const user = ref<any>(null)

  const isLoggedIn = computed(() => !!token.value && !!user.value)

  async function login(username: string, password: string) {
    const res = await api.post('/auth/login', { username, password })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('admin_token', token.value)
    return res.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('admin_token')
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
    } catch {
      logout()
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    logout,
    fetchProfile,
  }
})
