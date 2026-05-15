import axios from 'axios'
import { useAdminStore } from '@/stores/admin'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const adminStore = useAdminStore()
  if (adminStore.token) {
    config.headers.Authorization = `Bearer ${adminStore.token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const adminStore = useAdminStore()
      adminStore.logout()
    }
    return Promise.reject(err)
  }
)

export default api
