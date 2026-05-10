# AiMediaMaker - AI 图片与视频生成平台

基于火山方舟 API 的网页平台，支持调用 Seedance 2.0/2.0-fast 视频生成模型和 Seedream 5.0-lite/4.5 图片生成模型。

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Pinia + Vue Router + Tailwind CSS
- **后端**: Python + FastAPI + SQLAlchemy (async) + SQLite
- **缓存/队列**: Redis
- **文件存储**: 本地文件系统
- **AI API**: 火山方舟 (Volcengine Ark)

## 项目结构

```
AiMediamaker-webtool/
├── backend/              # 后端服务 (FastAPI)
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 配置、数据库
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic Schema
│   │   ├── services/     # 业务逻辑服务
│   │   └── main.py       # 应用入口
│   ├── storage/          # 本地文件存储
│   ├── requirements.txt
│   └── tests/
├── frontend/             # 前端 (Vue 3 + TS)
│   ├── src/
│   │   ├── api/          # API 客户端
│   │   ├── components/   # 组件
│   │   ├── stores/       # Pinia Store
│   │   ├── types/        # TypeScript 类型
│   │   └── views/        # 页面
│   ├── package.json
│   └── vite.config.ts
└── docs/                 # 文档
```

## 快速启动

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 创建 .env 文件配置环境变量
# 运行
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 核心功能

- 图片生成 (Seedream 5.0-lite / 4.5)
- 视频生成 (Seedance 2.0 / 2.0-fast)
- 多模态输入 (文本、图片、视频、音频参考)
- 任务队列管理与并发控制
- 用户历史任务与资产管理
- 文件预览与下载

## Git 分支策略

- `main`: 生产分支
- `develop`: 开发分支
- `feature/*`: 功能分支
- `release/*`: 发布分支
- `hotfix/*`: 热修复分支
