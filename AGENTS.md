# AiMediaMaker - Agent 开发指南

## 技术约束

- **数据库**: 必须使用 SQLite (aiosqlite)，不可引入 PostgreSQL/MySQL
- **文件存储**: 本地文件系统，`backend/storage/` 目录下
- **缓存/队列**: Redis (简单场景用，避免过度设计)
- **后端框架**: FastAPI + SQLAlchemy 2.0 (异步模式)
- **前端框架**: Vue 3 + TypeScript + Composition API
- **API 规范**: RESTful + JWT Bearer 认证

## 目录规范

### 后端
- 所有业务逻辑放在 `services/` 中，禁止在 router 中写业务逻辑
- 模型定义在 `models/`，使用 SQLAlchemy 2.0 声明式语法
- Schema 定义在 `schemas/`，使用 Pydantic v2
- API 路由按版本分目录 `api/v1/`

### 前端
- 组件使用 `<script setup lang="ts">`
- API 调用封装在 `src/api/index.ts`
- 状态管理使用 Pinia + Composition API
- 类型定义统一放在 `src/types/index.ts`

## 安全规范

- 所有文件访问必须验证 `user_id` 归属
- 密码使用 bcrypt 哈希
- JWT Token 有效期 7 天
- 上传文件类型白名单校验
- 文件大小限制 100MB

## 火山方舟 API 集成

- Base URL: `https://ark.cn-beijing.volces.com/api/v3`
- 视频生成: `POST /contents/generations/tasks`
- 视频查询: `GET /contents/generations/tasks/{id}`
- 图片生成: `POST /images/generations`
- API Key 通过环境变量注入，禁止硬编码

## 任务队列设计

- 使用 asyncio 实现异步任务轮询
- 每个模型独立并发计数器
- 默认 30 秒轮询间隔
- 任务状态: pending -> queued -> running -> succeeded/failed/cancelled
