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

## 任务管理

### POST /api/v1/tasks/create
- 请求: `{ mode, model_id, prompt, parameters?, file_ids? }`
- 响应: `TaskResponse`
- 说明: 创建任务并进入队列；file_ids对应的文件将自动处理为TOS URL或Base64

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
- 说明: 下载/预览文件，仅限自己的文件

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
