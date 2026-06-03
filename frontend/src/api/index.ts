import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      // 触发全局未授权事件，由 App.vue 等监听处理
      window.dispatchEvent(new CustomEvent('api:unauthorized'))
    }
    // 为常见错误添加友好的 message，方便业务层使用
    if (err.response?.status === 403) {
      err.message = err.response?.data?.detail || '权限不足，无法访问'
    } else if (err.response?.status === 404) {
      err.message = err.response?.data?.detail || '请求的资源不存在'
    } else if (err.response?.status >= 500) {
      err.message = err.response?.data?.detail || '服务器内部错误，请稍后重试'
    } else if (err.code === 'ECONNABORTED' || err.code === 'ETIMEDOUT') {
      err.message = '请求超时，请检查网络或稍后重试'
    }
    return Promise.reject(err)
  }
)

export default api
