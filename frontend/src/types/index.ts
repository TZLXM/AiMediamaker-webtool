/**
 * 核心类型定义
 */

// 用户
export interface User {
  id: number
  username: string
  role: 'admin' | 'leader' | 'user'
  is_active: boolean
  created_at: string
}

// 任务状态
export type TaskStatus =
  | 'pending'
  | 'queued'
  | 'running'
  | 'succeeded'
  | 'failed'
  | 'cancelled'
  | 'cancelling'
  | 'downloading'

export type TaskMode = 'image' | 'video'

// 任务参数
export interface TaskParameters {
  // 视频
  ratio?: string
  duration?: number
  resolution?: string
  fps?: number
  generate_audio?: boolean
  watermark?: boolean
  seed?: number
  // 图片
  aspectRatio?: string
  size?: string
  output_format?: string
  sequential_image_generation?: string
  max_images?: number
  // 通用
  extra?: Record<string, any>
  // 索引签名，支持动态参数 key
  [key: string]: any
}

// 文件
export interface FileItem {
  file_id: string
  original_name: string
  file_type: 'image' | 'video' | 'audio'
  mime_type: string
  size_bytes: number
  source: 'upload' | 'output' | 'base64'
  url: string
  thumbnail_url?: string
  public_url?: string
  created_at: string
}

// 任务
export interface TaskItem {
  id: number
  platform_task_id: string
  mode: TaskMode
  model_id: string
  prompt: string
  parameters?: TaskParameters
  status: TaskStatus
  error_code?: string
  error_message?: string
  remote_task_id?: string
  started_at?: string
  completed_at?: string
  usage_tokens?: number
  created_at: string
  input_files: FileItem[]
  output_files: FileItem[]
}

// 模型配置
export interface ParameterOption {
  name: string
  value: any
  label: string
  description?: string
}

export interface ParameterSchema {
  key: string
  label: string
  type: 'select' | 'number' | 'boolean' | 'text'
  required: boolean
  default?: any
  options?: ParameterOption[]
  min?: any
  max?: any
  description?: string
}

export interface ModelInfo {
  model_id: string
  name: string
  mode: TaskMode
  description?: string
  parameters: ParameterSchema[]
  supported_input_types: string[]
}

// 预览
export interface PreviewState {
  visible: boolean
  file?: FileItem
  isVideo: boolean
}

// 侧边栏
export type ViewType = 'generate' | 'history' | 'assets'
