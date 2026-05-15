import { useUserStore } from '@/stores/user'
import type { FileItem } from '@/types'

/**
 * 获取带鉴权 token 的文件访问 URL
 * 用于 img/video 等浏览器原生标签直接访问需要鉴权的资源
 */
export function getFileUrl(file: FileItem): string {
  const userStore = useUserStore()
  const token = userStore.token
  if (!token) return file.url
  const separator = file.url.includes('?') ? '&' : '?'
  return `${file.url}${separator}token=${token}`
}
