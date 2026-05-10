# AiMediaMaker - AI Agent 开发指南

> 本文档面向 AI Agent（如 Kimi、Claude、GPT 等），指导其正确理解项目结构、操作 Git、执行开发工作流。

---

## 一、项目概览（AI 必读）

**项目定位**：AI 图片与视频生成平台，通过火山方舟 API 调用 Seedance/Seedream 模型。

**核心数据流**：
```
用户上传文件 → 本地存储(FileManager) → TOS中转(TOSUploader) → 公网URL
                                    ↓
用户提交任务 → 任务队列(TaskQueue) → 火山方舟API → 下载结果 → 本地存储
```

**TOS 定位**：仅用于将参考文件转为公网 URL 供模型读取，不做备份。主存储始终在本地。

---

## 二、技术栈（不可变更）

| 层级 | 技术选型 | 变更限制 |
|------|---------|---------|
| 数据库 | SQLite (aiosqlite) | **严禁**引入 PostgreSQL/MySQL |
| 后端框架 | FastAPI + SQLAlchemy 2.0 (异步) | 保持 async/await 模式 |
| 缓存 | Redis | 仅用于任务状态/并发计数 |
| 文件存储 | 本地文件系统 | 主存储，TOS 只做中转 |
| 前端 | Vue 3 + TypeScript + Vite + Pinia | 必须使用 Composition API |
| AI API | 火山方舟 (Volcengine Ark) | Base URL 固定 |

---

## 三、目录结构与模块职责

```
backend/app/
├── api/v1/           # 路由层 - 只做参数校验和响应组装
│   ├── auth.py       # 登录/用户信息
│   ├── tasks.py      # 任务创建/查询/取消/历史
│   ├── files.py      # 文件上传/下载/资产列表
│   └── models.py     # 模型配置列表
├── core/             # 基础设施
│   ├── config.py     # 全局配置(Settings)，从.env读取
│   └── database.py   # 异步SQLite引擎 + 会话工厂
├── models/           # SQLAlchemy 2.0 ORM模型
│   ├── user.py       # User + UserRole(enum)
│   ├── task.py       # Task + TaskMode + TaskStatus(enum)
│   ├── file.py       # FileRecord + FileType + FileSource + StorageStatus(enum)
│   └── model_config.py # ApiConfig + ModelConfig + PlatformType + GenerationMode(enum)
├── schemas/          # Pydantic v2 校验模型
├── services/         # **业务逻辑层** - 所有核心逻辑在此
│   ├── model_manager.py    # 模型管理(并发/配置缓存)
│   ├── file_manager.py     # 本地文件存储(重命名/存取)
│   ├── file_processor.py   # 文件处理(Base64/TOS上传)
│   ├── tos_uploader.py     # TOS上传服务(火山引擎SDK)
│   ├── task_queue.py       # 异步任务队列(轮询/并发控制)
│   └── volcengine_client.py # 火山方舟API客户端
└── main.py           # FastAPI入口 + 生命周期管理
```

**关键规则**：
- `api/` 层 **禁止** 写业务逻辑，只能调用 `services/`
- `services/` 层 **禁止** 直接操作 HTTP Request/Response
- 新增功能时，优先在 `services/` 创建服务类，再在 `api/` 暴露路由

---

## 四、Git 工作流（AI 必须遵守）

### 4.1 分支策略

```
main        ← 生产分支，只接受 release/* 和 hotfix/* 合并
  ↑
develop     ← 开发主干，日常开发基于此
  ↑
feature/*   ← 功能分支，从 develop 切出，完成后合并回 develop
```

### 4.2 AI 操作 Git 的规范步骤

**Step 1: 确认当前分支**
```bash
git branch --show-current
```
- 如果不在 feature 分支，必须 `git checkout -b feature/xxx`
- **严禁**直接在 `main` 或 `develop` 上修改代码

**Step 2: 开发完成后提交**
```bash
git add -A
git status                    # AI必须确认修改内容后再提交
git commit -m "type: 简短描述

- 详细变更点1
- 详细变更点2"
```

**提交类型 (type)**：
| 类型 | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响逻辑） |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具链 |

**Step 3: 合并到 develop（需要用户确认）**
```bash
git checkout develop
git merge feature/xxx --no-ff
```
> ⚠️ **合并操作必须询问用户确认**，不可自行合并到 develop/main

### 4.3 AI 禁止的操作

- ❌ 禁止 `git push -f` (强制推送)
- ❌ 禁止在 `main` 分支直接修改代码
- ❌ 禁止提交 `.env` 文件（已被 .gitignore 排除，但需确认）
- ❌ 禁止提交包含真实 API Key 的代码
- ❌ 禁止 `git reset --hard` 丢弃他人提交

---

## 五、开发工作流（AI 执行步骤）

### 5.1 新增功能的标准流程

```
1. 阅读 docs/requirements.md 确认需求
2. 切出 feature/xxx 分支
3. 如需改数据库：
   a. 修改 models/xxx.py
   b. 运行 alembic revision --autogenerate -m "描述"
4. 如需新增接口：
   a. 在 schemas/ 新增 Pydantic 模型
   b. 在 services/ 新增/修改业务逻辑
   c. 在 api/v1/ 新增路由
5. 如需改前端：
   a. 在 src/types/ 新增类型
   b. 在 src/stores/ 新增/修改 Pinia store
   c. 在 src/components/ 或 src/views/ 实现组件
6. 编写/更新测试
7. 本地验证：
   - 后端: uvicorn app.main:app --reload
   - 前端: npm run dev
8. git add + git commit
9. 报告用户，请求合并
```

### 5.2 调试与验证

**后端调试**：
```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
# 访问 http://localhost:8000/docs 查看 Swagger API 文档
```

**前台前端调试**：
```bash
cd frontend
npm run dev
# 访问 http://localhost:5173
# API请求自动代理到 localhost:8000
```

**后台前端调试**：
```bash
cd frontend-admin
npm run dev
# 访问 http://localhost:5174
# API请求自动代理到 localhost:8000
# 仅 admin/leader 角色可登录后台
```

**数据库查看**：
```bash
# SQLite 直接查看
sqlite3 backend/app.db ".tables"
sqlite3 backend/app.db "SELECT * FROM users;"
```

---

## 六、代码规范（AI 必须遵守）

### 6.1 Python 规范

```python
# ✅ 正确：使用类型注解、异步模式
async def create_task(
    db: AsyncSession,
    user_id: int,
    mode: TaskMode,
) -> Task:
    ...

# ❌ 错误：缺少类型注解、同步模式
def create_task(db, user_id, mode):
    ...
```

- 所有函数必须有类型注解
- 所有数据库操作必须是 `async/await`
- SQLAlchemy 使用 2.0 风格：`select(Model).where(...)`
- Pydantic 使用 v2：`model_validate()` 而非 `from_orm()`

### 6.2 Vue/TS 规范

```vue
<!-- ✅ 正确 -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { TaskItem } from '@/types'

const props = defineProps<{ task: TaskItem }>()
const emit = defineEmits<['reuse']>()
</script>

<!-- ❌ 错误：不使用 Options API，不写 JS -->
<script>
export default {
  data() { return {} }
}
</script>
```

### 6.3 安全红线

| 红线 | 说明 |
|------|------|
| user_id 校验 | 任何查询必须带 `user_id == current_user.id` 条件 |
| 文件访问 | 文件下载必须验证归属，非本人返回 404 |
| API Key | 禁止硬编码，必须从 `settings.ARK_API_KEY` / 数据库读取 |
| SQL 注入 | 必须使用 SQLAlchemy ORM，禁止字符串拼接 SQL |
| XSS | 前端渲染用户输入内容时必须转义 |

---

## 七、常见问题（AI 自查清单）

### Q1: 修改了模型，数据库没有更新？
**解决**：
```bash
cd backend
alembic revision --autogenerate -m "描述"
alembic upgrade head
# 或在开发环境直接删除 app.db 重新 init_db()
```

### Q2: 新增的服务怎么注册？
**解决**：不需要注册。直接在 `api/` 路由中 `from app.services.xxx import xxx` 导入使用。全局单例已在模块级实例化。

### Q3: 前端请求后端返回 CORS 错误？
**解决**：检查 `backend/app/core/config.py` 中 `CORS_ORIGINS` 是否包含前端地址。开发环境默认包含 `http://localhost:5173`。

### Q4: TOS 上传失败？
**解决**：
1. 检查 `.env` 中 TOS 四个配置项是否已填
2. 检查 AK/SK 是否有该 Bucket 的读写权限
3. 检查网络是否能访问 `tos-cn-beijing.volces.com`
4. 查看后端日志的具体报错

### Q5: 任务状态不更新？
**解决**：
1. 检查 Redis 是否正常运行 (`redis-cli ping`)
2. 检查任务是否已分配 `remote_task_id`
3. 检查火山方舟 API Key 是否有效
4. 查看后端日志中的轮询请求和响应

---

## 八、模块依赖关系图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   api/v1/*.py   │────▶│   services/*.py │────▶│   models/*.py   │
│   (路由层)       │     │   (业务逻辑层)   │     │   (数据模型)     │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │  model_  │ │  file_   │ │  task_   │
            │  manager │ │  manager │ │  queue   │
            └──────────┘ └────┬─────┘ └──────────┘
                                │
                       ┌────────┴────────┐
                       ▼                 ▼
                ┌──────────┐      ┌──────────┐
                │  tos_    │      │ volcengine│
                │ uploader │      │  _client │
                └──────────┘      └──────────┘
```

**调用方向**：上层可调用下层，下层不可调用上层。
- `api/` → `services/` → `models/`
- `services/` 之间可横向调用（如 `task_queue` 调用 `file_manager`）

---

## 九、环境变量清单（AI 配置时必须检查）

```bash
# 后端 .env 必填项检查表
SECRET_KEY=           # 必须修改，不能留默认值
DATABASE_URL=         # 默认SQLite，通常无需修改
REDIS_URL=            # 默认localhost:6379
ARK_API_KEY=          # 火山方舟API Key，必填
TOS_ENDPOINT=         # 必填，默认 tos-cn-beijing.volces.com
TOS_ACCESS_KEY=       # 必填，火山引擎AK
TOS_SECRET_KEY=       # 必填，火山引擎SK
TOS_BUCKET=           # 必填，Bucket名称
```

> AI 在启动项目前，必须检查以上必填项是否已配置。
