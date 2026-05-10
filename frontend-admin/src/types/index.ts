/**
 * 后台管理 - 核心类型定义
 */

// 用户
export interface AdminUser {
  id: number
  username: string
  role: 'admin' | 'leader' | 'user'
  is_active: boolean
  created_at: string
}

// 模型配置
export interface ModelConfig {
  id: number
  name: string
  model_id: string
  mode: 'image' | 'video'
  description?: string
  concurrency_limit: number
  parameters_schema: ParameterSchema[]
  supported_input_types: string[]
  is_active: boolean
  sort_order: number
  created_at: string
}

export interface ParameterSchema {
  key: string
  label: string
  type: 'select' | 'number' | 'boolean' | 'text'
  required: boolean
  default?: any
  options?: { name: string; value: any; label: string }[]
  min?: any
  max?: any
  description?: string
}

// API配置
export interface ApiConfig {
  id: number
  name: string
  platform: string
  base_url: string
  total_concurrency: number
  is_active: boolean
  created_at: string
}

// 任务（管理视角）
export interface AdminTask {
  id: number
  platform_task_id: string
  user_id: number
  username: string
  mode: 'image' | 'video'
  model_id: string
  prompt: string
  status: string
  error_code?: string
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

// 系统状态
export interface SystemStatus {
  active_tasks: number
  queued_tasks: number
  total_users: number
  total_tasks: number
  disk_usage: number
  redis_connected: boolean
  tos_connected: boolean
}

// 菜单
export interface MenuItem {
  key: string
  label: string
  path: string
  icon: string
  children?: MenuItem[]
}
