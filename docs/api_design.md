# API 接口设计文档

## 文件处理流程说明 (TOS为必选项)

```
用户上传文件
    │
    ▼
┌─────────────────┐
│ 1. 本地文件存储  │  ← 文件管理模块 (FileManager)
│   (唯一命名)    │     存储到 backend/storage/uploads/
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. TOS上传      │  ← 文件处理模块 (FileProcessor) - 必选项
│   (异步/同步)   │     上传至火山引擎对象存储
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 获取公网URL   │  ← 存储到 file.public_url
│   (传给模型API)  │     状态: uploaded
└─────────────────┘
```

**TOS上传是平台运行的必选项**。原因：
- 火山方舟API要求参考文件的URL必须可公网访问
- Base64仅适用于小文件(≤5MB)，且会增加请求体大小
- TOS提供可靠的文件托管和访问控制

---

## 认证

所有 API (除登录外) 需携带 Header: `Authorization: Bearer {token}`

### POST /api/v1/auth/login
- 请求: `{ username, password }`
- 响应: `{ access_token, token_type, expires_in, user }`
- 说明: 仅支持已有账号登录，无注册接口

### GET /api/v1/auth/me
- 响应: `{ id, username, role, is_active, created_at }`

---

## 管理后台 (Admin Only)

所有 `/api/v1/admin/*` 接口需要 `admin` 角色，否则返回 403。

### POST /api/v1/admin/api-configs
- 请求: `{ name, platform, api_key, base_url?, total_concurrency?, is_active?, extra_config? }`
- 响应: `ApiConfigResponse`

### GET /api/v1/admin/api-configs
- 响应: `ApiConfigResponse[]`

### GET /api/v1/admin/api-configs/{id}
- 响应: `ApiConfigResponse`

### PUT /api/v1/admin/api-configs/{id}
- 请求: `{ name?, platform?, api_key?, base_url?, total_concurrency?, is_active?, extra_config? }`
- 响应: `ApiConfigResponse`
- 说明: 部分更新，未传字段保持不变

### DELETE /api/v1/admin/api-configs/{id}
- 状态码: 204
- 说明: 删除后自动刷新 model_manager 缓存

### POST /api/v1/admin/model-configs
- 请求: `{ name, model_id, api_config_id, mode, description?, concurrency_limit?, parameters_schema?, supported_input_types?, is_active?, sort_order? }`
- 响应: `ModelConfigResponse`
- 说明: 检查 `api_config_id` 存在性和 `model_id` 唯一性

### GET /api/v1/admin/model-configs
- 响应: `ModelConfigResponse[]`

### GET /api/v1/admin/model-configs/{id}
- 响应: `ModelConfigResponse`

### PUT /api/v1/admin/model-configs/{id}
- 请求: 同创建，全部字段可选
- 响应: `ModelConfigResponse`
- 说明: 更新 `model_id` 时检查唯一性；`parameters_schema` 自动序列化

### DELETE /api/v1/admin/model-configs/{id}
- 状态码: 204
- 说明: 删除后自动刷新 model_manager 缓存

---

## 任务管理

### POST /api/v1/tasks/create
- 请求: `{ mode, model_id, prompt, parameters?, file_ids? }`
- 响应: `TaskResponse`
- 说明: 创建任务并立即启动异步处理；`file_ids` 对应的文件将自动通过 `file_processor.prepare_for_model()` 处理为 TOS URL 或 Base64；任务先进入 `QUEUED` 状态，获取并发槽位后变为 `RUNNING`

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

---

## 文件管理

### POST /api/v1/files/upload
- 请求: `multipart/form-data` (file)
- 响应: `FileUploadResponse`
- 说明: 
  - 上传文件到本地存储
  - **自动触发TOS异步上传**
  - 返回的 `url` 为本地预览地址，后续 `public_url` 为TOS公网地址

### GET /api/v1/files/{file_id}
- 响应: 文件流 (FileResponse)
- 说明: 下载/预览文件，仅限自己的文件；`download=true` 时触发下载

### GET /api/v1/files/{file_id}/preview
- 参数: `?width=` (64-1920, 默认 512)
- 响应: 文件流/缩略图
- 说明: 图片返回 Pillow 缩略图；视频/音频返回原文件

### DELETE /api/v1/files/{file_id}
- 状态码: 204
- 说明: 删除文件（仅限自己的文件），同时删除本地文件和 DB 记录

### GET /api/v1/files/assets/list
- 参数: `?file_type=&search=&page=&page_size=`
- 响应: `FileResponse[]`
- 说明: 获取模型生成的资产列表

---

## 模型配置

### GET /api/v1/models/list
- 参数: `?mode=`
- 响应: `ModelSelectorInfo[]`
- 说明: 获取可用模型列表及参数配置；前端根据 `parameters` 动态渲染表单
