# AiMediaMaker 部署指南

## 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 后端运行时 |
| Node.js | 18+ | 前端构建 |
| Redis | 6.0+ | 缓存与并发控制 |
| Git | 2.30+ | 代码管理 |

> Windows 部署 Redis：下载 [Redis-64](https://github.com/MicrosoftArchive/redis/releases) 或使用 WSL。

---

## 一、获取代码

```bash
git clone <仓库地址> AiMediamaker-webtool
cd AiMediamaker-webtool
git checkout feature/m3-frontend   # 或你要部署的分支
```

---

## 二、后端部署

### 2.1 创建虚拟环境

```bash
cd backend

# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2.2 安装依赖

```bash
pip install -r requirements.txt
```

### 2.3 配置环境变量

复制模板并编辑：

```bash
cp .env.example .env        # macOS/Linux
copy .env.example .env      # Windows
```

编辑 `.env`，**必须填写以下项**：

```env
# 应用密钥（生产环境必须修改为随机长字符串）
SECRET_KEY=your-random-secret-key-here

# Redis（确保 Redis 服务已启动）
REDIS_URL=redis://localhost:6379/0

# 火山方舟 API Key（从火山引擎控制台获取）
ARK_API_KEY=your-ark-api-key

# TOS 对象存储（必填，用于文件中转）
TOS_ENDPOINT=tos-cn-beijing.volces.com
TOS_ACCESS_KEY=your-access-key
TOS_SECRET_KEY=your-secret-key
TOS_BUCKET=your-bucket-name
TOS_REGION=cn-beijing
```

> 生产环境请修改：
> - `DEBUG=false`
> - `SECRET_KEY` 改为强随机字符串
> - `CORS_ORIGINS` 改为你的实际域名

### 2.4 初始化数据库

```bash
python scripts/init_data.py
```

会自动创建：
- SQLite 数据库表
- 默认用户：`admin/admin123`、`leader/leader123`、`user1/user123`
- 模型配置模板

### 2.5 启动后端（开发模式）

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

生产模式（去掉 `--reload`，建议配合 systemd/supervisor）：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

---

## 三、前端部署

### 3.1 安装依赖

```bash
cd frontend
npm install
cd ../frontend-admin
npm install
```

### 3.2 构建生产包

```bash
# 构建前台
cd frontend
npm run build

# 构建后台
cd ../frontend-admin
npm run build
```

构建产物：
- `frontend/dist/` — 用户前台
- `frontend-admin/dist/` — 后台管理

### 3.3 验证静态文件挂载

后端启动时会自动检测并挂载：
- `http://localhost:8000/` → 用户前台
- `http://localhost:8000/admin` → 后台管理
- `http://localhost:8000/api` → API 接口

> 如果 `frontend-admin/dist` 或 `frontend/dist` 不存在，后端只会启动 API 服务。

---

## 四、访问验证

### 开发模式（前后端分离）

| 服务 | 地址 | 说明 |
|------|------|------|
| 前台页面 | http://localhost:5173 | `cd frontend && npm run dev` |
| 后台管理 | http://localhost:5174 | `cd frontend-admin && npm run dev` |
| API 接口 | http://localhost:8000 | 后端服务 |

### 生产模式（单端口）

| 服务 | 地址 | 说明 |
|------|------|------|
| 前台页面 | http://localhost:8000 | 后端挂载静态文件 |
| 后台管理 | http://localhost:8000/admin | 后端挂载静态文件 |
| API 接口 | http://localhost:8000/api | 后端服务 |

---

## 五、内网穿透/公网访问

### 方式一：只穿透前端（开发调试）

启动前后端分离服务，然后穿透前端端口：

```bash
# 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前台（新终端）
cd frontend && npm run dev

# 启动后台（新终端）
cd frontend-admin && npm run dev
```

用 ngrok/frp 穿透 `5173` 和 `5174`：

```bash
ngrok http 5173    # 前台
ngrok http 5174    # 后台
```

> DEBUG=true 时后端自动允许任意 Origin，无需手动配置 CORS。

### 方式二：只穿透后端（生产部署）

构建前端后只启动后端，穿透 `8000`：

```bash
cd frontend && npm run build
cd ../frontend-admin && npm run build
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

```bash
ngrok http 8000
```

一个穿透地址同时提供前台 + 后台 + API。

---

## 六、Docker 部署（可选）

如需 Docker 部署，项目需要补充 `Dockerfile` 和 `docker-compose.yml`，可向开发者索取或自行编写。

核心思路：
1. 多阶段构建：Node 构建前端 → Python 运行后端
2. 将 `frontend/dist` 和 `frontend-admin/dist` 复制到 backend 目录下
3. 单容器暴露 8000 端口

---

## 七、常见问题

### Q1: 启动后端报错 "Redis connection failed"
确保 Redis 服务已启动：
```bash
# Windows
redis-server.exe

# Linux/macOS
redis-server
```

### Q2: 访问 `/admin` 404
确保已执行 `cd frontend-admin && npm run build`，且 `frontend-admin/dist` 目录存在。

### Q3: 内网穿透后页面显示 "Blocked request"
已修复。如仍遇到，确认 `vite.config.ts` 中有 `allowedHosts: true`。

### Q4: 内网穿透后 API 请求 CORS 报错
确保 `.env` 中 `DEBUG=true`。生产环境（DEBUG=false）时需在 `CORS_ORIGINS` 中手动添加穿透域名。

### Q5: 上传文件失败
检查 `.env` 中 TOS 配置是否正确。TOS 是文件上传的必选项。

---

## 八、文件清单（部署前检查）

```
backend/
  ├── .env                  ✅ 已配置
  ├── .venv/                ✅ 虚拟环境
  ├── app.db                ✅ 数据库（init_data.py 后生成）
  ├── storage/              ✅ 本地存储目录
  ├── requirements.txt      ✅ 依赖列表
  └── scripts/init_data.py  ✅ 初始化脚本

frontend/
  └── dist/                 ✅ npm run build 后生成

frontend-admin/
  └── dist/                 ✅ npm run build 后生成
```
