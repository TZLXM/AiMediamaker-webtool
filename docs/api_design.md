# API 接口设计文档

## 认证

所有 API (除登录外) 需携带 Header: `Authorization: Bearer {token}`

### POST /api/v1/auth/login
- 请求: `{ username, password }`
- 响应: `{ access_token, token_type, expires_in, user }`
- 说明: 仅支持已有账号登录，无注册接口

### GET /api/v1/auth/me
- 响应: `{ id, username, role, is_active, created_at }`

## 任务管理

### POST /api/v1/tasks/create
- 请求: `{ mode, model_id, prompt, parameters?, file_ids? }`
- 响应: `TaskResponse`
- 说明: 创建任务并进入队列

### GET /api/v1/tasks/{platform_task_id}
- 响应: `TaskResponse`
- 说明: 查询任务状态，仅限自己的任务

### POST /api/v1/tasks/{platform_task_id}/cancel
- 响应: `{ success, message }`
- 说明: 取消任务，仅限自己的任务

### GET /api/v1/tasks/history/list
- 参数: `?mode=&search=&page=&page_size=`
- 响应: `TaskResponse[]`
- 说明: 获取已结束任务历史

## 文件管理

### POST /api/v1/files/upload
- 请求: `multipart/form-data` (file)
- 响应: `FileUploadResponse`
- 说明: 上传文件，校验类型和大小

### GET /api/v1/files/{file_id}
- 响应: 文件流 (FileResponse)
- 说明: 下载/预览文件，仅限自己的文件

### GET /api/v1/files/assets/list
- 参数: `?file_type=&search=&page=&page_size=`
- 响应: `FileResponse[]`
- 说明: 获取模型生成的资产列表

## 模型配置

### GET /api/v1/models/list
- 参数: `?mode=`
- 响应: `ModelSelectorInfo[]`
- 说明: 获取可用模型列表及参数配置
