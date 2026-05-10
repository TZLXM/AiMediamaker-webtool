# 开发环境搭建与测试指南

## 环境要求

- **Python**: 3.10+
- **Node.js**: 18+
- **Redis**: 6.0+ (Windows可用Redis-64或WSL)
- **Git**: 2.30+

---

## 第一步：克隆项目并切换分支

```bash
git clone <repository-url> AiMediamaker-webtool
cd AiMediamaker-webtool
git checkout develop
git checkout -b feature/your-feature-name
```

---

## 第二步：后端环境搭建

### 2.1 创建Python虚拟环境

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

# TOS上传是必选项，必须安装火山引擎TOS SDK
pip install tos
```

### 2.3 配置环境变量

复制环境模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写以下**必填项**：

```env
# 应用配置
SECRET_KEY=your-random-secret-key-here  # 生产环境必须修改

# 数据库 (默认SQLite，无需修改)
DATABASE_URL=sqlite+aiosqlite:///{项目绝对路径}/backend/app.db

# Redis
REDIS_URL=redis://localhost:6379/0

# 火山方舟API (必填)
ARK_API_KEY=your-ark-api-key-here

# TOS对象存储 (必填 - 平台核心依赖)
TOS_ENDPOINT=tos-cn-beijing.volces.com
TOS_ACCESS_KEY=your-tos-access-key
TOS_SECRET_KEY=your-tos-secret-key
TOS_BUCKET=your-bucket-name
TOS_REGION=cn-beijing
```

> ⚠️ **TOS是平台运行的必选项**。没有TOS配置，文件无法传递给火山方舟API进行多模态生成。
> 
> 获取方式：
> 1. 登录 [火山引擎控制台](https://console.volcengine.com)
> 2. 进入 "对象存储TOS" 创建Bucket
> 3. 在 "访问控制" 创建AK/SK密钥对

### 2.4 初始化数据库与种子数据

```bash
# 初始化数据表
python -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"

# 插入种子数据 (默认admin账号、模型配置)
python scripts/init_data.py
```

种子数据包含：
- 管理员账号: `admin` / `admin123` (首次登录后请修改密码)
- 测试用户: `user1` / `user123`
- 模型配置: Seedance 2.0, Seedance 2.0 Fast, Seedream 5.0 Lite, Seedream 4.5
- API配置模板 (需手动填入API Key)

### 2.5 启动后端服务

```bash
# 开发模式 (热重载)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

验证启动成功：
- 浏览器访问 `http://localhost:8000/health` → 返回 `{"status":"ok"}`
- 访问 `http://localhost:8000/docs` → Swagger API文档页面

---

## 第三步：前端环境搭建

### 3.1 安装依赖

```bash
cd frontend

# 如果npm执行策略受限，使用npx
npx npm install

# 或直接安装 (PowerShell需先设置执行策略)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
npm install
```

### 3.2 启动开发服务器

```bash
npm run dev
```

前端将启动在 `http://localhost:5173`，并自动代理 `/api` 请求到后端的 `8000` 端口。

---

## 第四步：Redis启动

### Windows (使用WSL或预编译二进制)

```powershell
# 方式1: 使用WSL
wsl -d Ubuntu -e redis-server

# 方式2: 使用预编译的Redis-x64
# 下载后运行: redis-server.exe redis.windows.conf
```

### macOS

```bash
brew install redis
brew services start redis
```

### Linux

```bash
sudo apt install redis-server
sudo systemctl start redis
```

验证Redis连接：
```bash
redis-cli ping  # 应返回 PONG
```

---

## 第五步：全流程功能测试

### 测试1: 登录流程

```bash
# 使用curl测试
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 期望返回: {"access_token":"...","token_type":"bearer","expires_in":604800,"user":{...}}
```

### 测试2: 文件上传 + TOS上传

```bash
# 1. 先登录获取token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# 2. 上传测试图片
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/test.jpg"

# 3. 验证数据库中 file.public_url 有值
# 4. 验证TOS桶中出现了对应对象
```

### 测试3: 图片生成全流程

```bash
# 1. 获取可用模型列表
curl http://localhost:8000/api/v1/models/list?mode=image \
  -H "Authorization: Bearer $TOKEN"

# 2. 创建图片生成任务
curl -X POST http://localhost:8000/api/v1/tasks/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "image",
    "model_id": "doubao-seedream-5-0-lite-260128",
    "prompt": "一只可爱的橘猫在草地上打滚",
    "parameters": {"size":"2K","output_format":"png"},
    "file_ids": []
  }'

# 3. 轮询查询任务状态
curl http://localhost:8000/api/v1/tasks/{platform_task_id} \
  -H "Authorization: Bearer $TOKEN"
```

### 测试4: 视频生成全流程 (含参考文件)

```bash
# 1. 先上传参考图片 (获取 file_id)
# 2. 创建视频生成任务
curl -X POST http://localhost:8000/api/v1/tasks/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "video",
    "model_id": "doubao-seedance-2-0-260128",
    "prompt": "画面中的猫咪动了起来的特写镜头",
    "parameters": {"ratio":"16:9","duration":5,"generate_audio":true},
    "file_ids": ["file_xxx"]
  }'
```

### 测试5: 权限隔离验证

```bash
# 1. 用user1登录创建任务
# 2. 用admin登录尝试访问user1的任务
# 3. 期望返回 404 (不能看到他人任务)
```

---

## 第六步：运行测试套件

### 后端单元测试

```bash
cd backend
pytest tests/ -v --tb=short

# 带覆盖率
pytest tests/ --cov=app --cov-report=html
```

### 前端构建测试

```bash
cd frontend
npm run build
# 验证 dist/ 目录生成且无报错
```

---

## 常见问题排查

### Q: `ModuleNotFoundError: No module named 'tos'`
**解决**: TOS是必选项，必须执行 `pip install tos`。这是火山引擎官方SDK。

### Q: `RuntimeError: TOS配置不完整`
**解决**: 检查 `.env` 文件中 `TOS_ACCESS_KEY`, `TOS_SECRET_KEY`, `TOS_BUCKET`, `TOS_ENDPOINT` 是否都已填写。

### Q: Redis连接失败
**解决**: 
- Windows: 确认WSL中redis-server已启动，或安装 [Redis-x64](https://github.com/tporadowski/redis/releases)
- 检查 `.env` 中 `REDIS_URL` 是否匹配实际Redis地址

### Q: 前端代理到后端失败
**解决**: 检查 `frontend/vite.config.ts` 中 proxy 配置；确认后端确实运行在 `8000` 端口。

### Q: SQLite数据库锁定
**解决**: 这是SQLite的并发限制。确保使用 `aiosqlite` + WAL模式已启用。高并发场景考虑切换到PostgreSQL。

### Q: 文件上传成功但TOS上没有
**解决**: 
1. 检查AK/SK是否有TOS写入权限
2. 检查Bucket是否开启了公共读 (或使用的是预签名URL)
3. 查看后端日志中的具体报错信息

---

## 开发工作流

### 日常开发步骤

```bash
# 1. 确保在feature分支
git status  # 应为 feature/xxx

# 2. 启动Redis (如果未后台运行)
redis-server

# 3. 启动后端 (终端1)
cd backend
.venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --port 8000

# 4. 启动前端 (终端2)
cd frontend
npm run dev

# 5. 访问 http://localhost:5173 开始开发
```

### 提交代码规范

```bash
# 提交前检查
git add .
git diff --cached --stat  # 确认修改内容

# 提交信息格式
git commit -m "feat: 添加视频生成参数选择器

- 支持ratio/duration/fps参数动态渲染
- 根据模型配置过滤不支持参数
- 修复切换模型时参数未清空的问题"

# 提交类型: feat/fix/docs/style/refactor/test/chore
```

### 合并到develop

```bash
git checkout develop
git pull origin develop
git merge feature/your-feature-name
# 解决冲突后
git push origin develop
```
