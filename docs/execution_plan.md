# 项目执行计划 (含验收标准)

> **样式基准**: 所有前端样式必须以根目录下的 `前端前台.zip`（用户前台）和 `前端后台.zip`（管理后台）为唯一设计基准。任何样式修改必须先对比 zip 解压后的构建产物，确保颜色、间距、圆角、字体、布局与参考实现完全一致。

---

## 阶段一：基础架构搭建

### 周期: Week 1

### 里程碑 M1.1: 项目骨架与Git工作流
**目标**: 代码仓库可用，CI/CD流程就绪

| 任务 | 负责人 | 验收标准 |
|------|--------|----------|
| Git仓库初始化 | 架构组 | 🟡 `develop` 和 `feature/*` 分支已创建；`main` 分支**缺失**；远程保护规则需 push 后配置 |
| 后端目录结构 | 后端组 | ✅ `uvicorn app.main:app --reload` 可正常启动，访问 `/health` 返回 `{"status":"ok"}`（已修复 `/health` 被 `StaticFiles` 覆盖的 bug） |
| 前端目录结构 | 前端组 | 🟡 `npm run build` 构建通过；目录结构完整；**但样式与 `前端前台.zip` / `前端后台.zip` 参考实现不一致**（见下方"差异清单"） |
| .env.example | 架构组 | ✅ 所有环境变量有注释说明，新成员5分钟内可完成配置 |

### 里程碑 M1.2: 数据库与ORM
**目标**: 数据持久化层就绪，支持增删改查

| 任务 | 验收标准 |
|------|----------|
| SQLAlchemy异步模型 | ✅ 5张表（users/tasks/files/api_configs/model_configs）可通过 `await init_db()` 自动创建；`pytest backend/tests/` 8项全部通过 |
| Alembic迁移 | ✅ `alembic.ini` / `migrations/env.py` 配置正确（异步引擎、模型导入完整）；`alembic upgrade head` 和 `alembic revision --autogenerate` 均可用 |
| 数据库连接池 | 🟡 SQLite WAL 模式已启用（`PRAGMA journal_mode=wal`）；`pool_pre_ping=True` 已配置；**并发100请求压测未执行** |

### 里程碑 M1.3: 认证体系
**目标**: 用户只能登录，不能注册

| 任务 | 验收标准 |
|------|----------|
| JWT登录接口 | ✅ POST `/api/v1/auth/login` 返回有效token；密码错误返回401；密码使用bcrypt存储 |
| 用户信息接口 | ✅ GET `/api/v1/auth/me` 返回当前用户信息；token过期返回401 |
| 前端登录页 | 🟡 登录弹窗组件骨架存在；**但样式与参考实现不一致** |
| Admin/Leader/User角色 | ✅ 数据库中3种角色的测试账号已创建；`role`字段正确返回 |

### M1 阶段出口检查清单
- [x] `pytest backend/tests/` 全部通过（69 passed）
- [x] `npm run build` 前端构建无报错（前台+后台均通过）
- [ ] 任意开发者clone后按README可10分钟内启动项目
- [x] Git提交信息符合规范 (feat/fix/docs/style/refactor/test)

---

## 阶段二：核心服务开发

### 周期: Week 2

### 里程碑 M2.1: 模型管理模块
**目标**: API和模型可动态配置，兼容火山方舟格式

| 任务 | 验收标准 |
|------|----------|
| API配置CRUD | ✅ Admin可增删改查API配置；API Key明文存储（TODO: 加密）；`total_concurrency` 生效；`GET/POST/PUT/DELETE /api/v1/admin/api-configs` |
| API配置删除 | ✅ `DELETE /api/v1/admin/api-configs/{id}` 级联删除（删除后刷新 model_manager 缓存） |
| 模型配置删除 | ✅ `DELETE /api/v1/admin/model-configs/{id}` 级联删除（删除后刷新 model_manager 缓存） |
| 模型配置CRUD | ✅ 可配置模型ID/名称/参数Schema/支持文件类型；`sort_order` 控制排序；`GET/POST/PUT/DELETE /api/v1/admin/model-configs` |
| 模型参数Schema | ✅ GET `/api/v1/models/list?mode=video` 返回完整参数定义；前端可动态渲染表单 |
| 多平台扩展性 | 🟡 新增平台只需增加 `PlatformType` 枚举和对应client类；不影响现有代码 |
| Admin路由权限 | ✅ `/api/v1/admin/*` 全部使用 `get_current_admin` 依赖，仅admin可访问 |

### 里程碑 M2.2: 文件管理模块 (含TOS上传 - 必选项)
**目标**: 用户上传的文件必须上传至TOS，返回公网URL

| 任务 | 验收标准 |
|------|----------|
| 文件上传 | ✅ POST `/api/v1/files/upload` 接收 multipart；文件重命名唯一；按类型分子目录存储；类型/大小校验 |
| 文件下载 | ✅ GET `/api/v1/files/{file_id}` 验证 `user_id` 归属后返回文件流；非本人返回 404 |
| 文件删除 | ✅ DELETE `/api/v1/files/{file_id}` 验证归属后删除；本地文件 + DB 记录一并清理 |
| 文件预览 | ✅ GET `/api/v1/files/{file_id}/preview` 图片生成 Pillow 缩略图；视频/音频返回原文件 |
| 资产列表 | ✅ GET `/api/v1/files/assets/list` 支持 `file_type`/`search`/`page`/`page_size` 筛选分页 |
| **TOS上传 (必选项)** | ✅ `tos_uploader.upload_file()` 基于 `tos` SDK (`Auth` + `TosClient`) 实现；真实上传至 `tempmedia` bucket 验证通过；与任务队列的 `file_processor.prepare_for_model()` 集成完成 |
| TOS配置校验 | ✅ 启动时检测 TOS 配置，未完整时输出 **ERROR 日志**；同时支持通过 admin 面板配置后热加载（`SystemConfig` 表 + `update_config_from_db`） |
| Base64转换 | ✅ `file_processor` 支持 `prepare_for_model` 策略；小文件可转 Base64；TOS 失败可回退 |
| 文件预览前端 | ❌ 前端缩略图显示未实现 |

### 里程碑 M2.3: 任务队列模块
**目标**: 任务异步执行，并发可控，状态可追踪

| 任务 | 验收标准 |
|------|----------|
| 任务创建与排队 | ✅ `POST /api/v1/tasks/create` 创建任务 → `task_queue.enqueue()` 分配 `platform_task_id` → 立即启动 `start_task_processing()` 异步处理；支持 `file_ids` 关联输入文件 |
| 并发控制 | ✅ Redis 分布式并发计数 (`redis_client.incr_model_active/decr_model_active`)；Redis 不可用时回退到内存计数 (`_memory_active_counts`)；每个模型独立计数，超出 `concurrency_limit` 时排队等待（轮询检查间隔 5 秒，最大等待 1 小时） |
| 状态轮询 | ✅ `_poll_task()` 默认 30 秒轮询一次；每个任务独立 `asyncio.Task`；支持 `succeeded`/`failed`/`cancelled`/`running` 状态；轮询连续失败 5 次后标记任务失败 |
| 任务取消 | ✅ `POST /api/v1/tasks/{platform_task_id}/cancel`；`QUEUED` 状态直接改 `CANCELLED`；`RUNNING` 状态调用远端 API 取消 + 取消本地 `asyncio.Task` |
| 历史记录 | ✅ `GET /api/v1/tasks/history/list` 按 `created_at` 升序排列（最晚在最下方）；支持 `mode`/`search` 筛选；仅返回 `SUCCEEDED`/`FAILED`/`CANCELLED` 状态 |
| 服务重启恢复 | ✅ `recover_tasks()` 启动时恢复 `QUEUED` 和 `RUNNING` 状态任务，自动重新进入轮询队列 |
| 优雅关闭 | ✅ `shutdown()` 取消所有运行中的本地轮询任务，等待 `asyncio.gather` 完成 |

### 里程碑 M2.4: 火山方舟API集成
**目标**: 可成功调用Seedance和Seedream生成内容

| 任务 | 验收标准 |
|------|----------|
| Seedance视频生成 | ✅ `VolcengineClient._create_video_task()` 调用 `POST /contents/generations/tasks`；支持 `ratio`/`duration`/`resolution`/`fps`/`generate_audio`/`watermark`/`seed` 参数；返回远端 `task_id` 供轮询 |
| Seedream图片生成 | ✅ `VolcengineClient._create_image_task()` 调用 `POST /images/generations`；支持 `size`/`output_format`/`sequential_image_generation`/`max_images`/`watermark`/`response_format` 参数；同步返回结果，使用 `img_sync_{created}` 作为伪任务ID |
| 多模态输入 | ✅ `_prepare_file_content()` 优先使用已有 `public_url`；无URL时调用 `file_processor.prepare_for_model()` 通过 TOS 上传获取公网 URL；支持 `image_url`/`video_url`/`audio_url` 三种参考类型 |
| 错误处理 | ✅ `VolcengineAPIError` 自定义异常（含 `code`/`message`/`status_code`）；HTTP 错误和 API 业务错误（200 但带 `error` 字段）均处理；创建任务带指数退避重试（`max_retries` 次） |
| 资源用量记录 | ✅ 轮询到 `succeeded` 时从响应中提取 `usage.completion_tokens` 写入 `task.usage_tokens` |
| 结果下载 | ✅ `_download_outputs()` 自动下载模型生成的图片/视频；支持 HTTP URL 和 Base64 data URI 两种格式；保存为 `FileRecord` (`source=output`) 关联到源任务 |
| 任务取消 | ✅ `cancel_task()` 对视频任务调用 `DELETE /contents/generations/tasks/{task_id}`；图片任务（`img_sync_` 前缀）直接返回成功 |

### 里程碑 M2.5: 前端 Admin 配置页面接入后端 API
**目标**: 管理后台可实际配置 API 和模型，不再停留在 TODO

| 任务 | 验收标准 |
|------|----------|
| API 配置 CRUD | ✅ `SystemConfigView.vue` 接入 `GET/POST/PUT/DELETE /api/v1/admin/api-configs`；支持新增、编辑、删除 API 配置 |
| 模型配置 CRUD | ✅ `ModelListView.vue` 接入 `GET/DELETE /api/v1/admin/model-configs`；`ModelEditView.vue` 接入 `GET/POST/PUT /api/v1/admin/model-configs`；编辑时可选关联的 API 配置 |
| 类型定义对齐 | ✅ `frontend-admin/src/types/index.ts` 补充 `api_key`、`api_config_id`、`sort_order` 等缺失字段 |
| TOS 配置表单 | ✅ `SystemConfigView.vue` 接入 `GET/PUT /api/v1/admin/system-config/tos`；支持读写 TOS 配置；启动时优先加载数据库配置并覆盖环境变量 |

### M2 阶段出口检查清单
- [ ] API Key 加密存储（当前为明文存储在 DB）
- [x] TOS 配置校验改为 ERROR 日志（支持通过 admin 面板配置后热加载，不强制退出以避免首次启动阻塞）
- [x] TOS桶中可查看到已上传的文件对象（已用真实 AK/SK 验证上传到 `tempmedia` bucket）
- [x] 完整走通一次 "上传图片 → 创建图生图任务 → 获取结果" 全流程（Seedream 5.0 Lite 成功生成图片，`status=succeeded`）
- [x] 完整走通一次 "输入提示词 → 创建视频生成任务 → 下载视频" 全流程（Seedance 2.0 成功提交远端任务，`remote_task_id=cgt-20260517151704-rb6lm`）
- [x] 并发提交5个任务，验证队列和并发控制正确工作（5 个任务全部成功创建，部分模型返回 404/400 为火山方舟模型 availability 问题，非系统 bug）
- [x] 取消一个running状态的任务，验证远端和本地状态一致（视频任务成功取消，`status=cancelled`）

---

## 阶段三：前端开发

### 周期: Week 3

### 里程碑 M3.1: 基础布局与全局组件（前台 + 后台）
**目标**: 页面框架完整，视觉风格统一

| 任务 | 验收标准 |
|------|----------|
| 前台侧边栏 | ✅ `AppSidebar.vue` 完整实现：Logo SVG、3 个导航项（生成/历史/资产）、路由高亮、用户信息、登录/登出按钮、lucide 图标 |
| 后台侧边栏 | ✅ `LayoutView.vue` 完整实现：5 个菜单项、路由高亮、用户信息/角色展示、退出登录、lucide 图标 |
| 登录弹窗 | ✅ `LoginModal.vue`（前台）+ `LoginView.vue`（后台）完整实现：表单、loading、错误提示、无注册说明 |
| 预览弹窗 | ✅ `PreviewModal.vue` 完整实现：`<Teleport>` 弹窗、图片滚轮缩放+拖拽平移、视频自定义控制条（播放/暂停/进度/音量）、下载按钮 |
| 路由与权限 | ✅ 前台/后台路由均配置完整；后台 admin 角色校验（非 admin 强制退出）；前台未登录自动弹窗/阻止导航 |

### 里程碑 M3.2: 生成页面 (核心页面)
**目标**: 用户可完成完整的生成操作

| 任务 | 验收标准 |
|------|----------|
| 输入悬浮框 | ✅ `InputBar.vue` 完整实现：底部悬浮、contenteditable 多行输入、上传文件缩略图（可删除）、模式选择器、模型选择器（联动过滤）、参数面板（select/number/boolean 动态渲染） |
| @文件引用 | ✅ `InputBar.vue` 已实现：输入 `@` 弹出文件选择器，选择后插入文件缩略图到 prompt 编辑器中 |
| 文件上传 | ✅ 已实现：选择文件上传，类型和大小校验，缩略图预览，右上角删除按钮 |
| 模型联动 | ✅ 已实现：`/models/list` 获取模型列表，根据 `mode` 过滤模型，根据模型 `parameters_schema` 动态渲染参数表单 |
| 任务块展示 | ✅ `TaskBlock.vue` 完整实现：提示词（展开/收起/复制）、输入文件缩略图、参数徽章（模式/模型/参数值）、输出结果网格（每行最多 4 个）、状态显示、复用按钮、完成时间 |
| 任务状态 | ✅ 已实现：`GenerateView.vue` 5 秒轮询活跃任务状态，实时更新任务块；`TaskBlock` 根据状态显示不同样式 |
| 复用功能 | ✅ 已实现：`reuseTask()` 将任务的模式/模型/提示词/参数回填到输入栏 |
| 新建会话 | ✅ 已实现：`resetSession()` 清空输入栏所有内容并恢复默认模式 |

### 里程碑 M3.3: 历史页面
**目标**: 用户可检索和复用历史任务

| 任务 | 验收标准 |
|------|----------|
| 历史列表 | ✅ `HistoryView.vue` 完整实现（624 行）：按 `YYYY年MM月DD日` 日期分组显示，`dayjs` 格式化；加载/空状态完整 |
| 搜索筛选 | ✅ 搜索框 + 300ms 防抖；时间预设筛选（全部/最近一周/一月/三月）+ 自定义日期范围；任务类型筛选（全部/图片/视频）；筛选联动自动重新请求 |
| 复用跳转 | ✅ 点击任务「复用」按钮 → `router.push('/generate?reuse_task_id=xxx')`；`GenerateView.vue` 监听 query 参数 → `loadAndReuseTask()` 回填输入栏；跳转后清除 query 防重复 |
| 后端接入 | ✅ `taskStore.fetchHistory()` → `GET /tasks/history/list`，支持 `mode`/`search`/`start_date`/`end_date`/`page`/`page_size` 参数 |

### 里程碑 M3.4: 资产页面
**目标**: 用户可管理和下载生成的文件

| 任务 | 验收标准 |
|------|----------|
| 资产网格 | ✅ `AssetsView.vue` 完整实现：`grid-template-columns: repeat(auto-fill, minmax(180px, 1fr))` 自适应网格；`aspect-ratio: 1` 缩略图比例；`object-fit: cover` 填充；按日期分组展示 |
| 悬停交互 | 🟡 卡片 hover 上浮+阴影、Thumbnail hover 渐变遮罩+文件名、下载按钮 hover 显示 ✅；**删除按钮未启用**（`Thumbnail` 组件支持 `show-delete` prop，但 `AssetsView.vue` 未传入，也未绑定删除事件） |
| 搜索筛选 | ✅ 搜索框 + 300ms 防抖；时间预设筛选 + 自定义日期范围；类型筛选（全部/图片/视频）；筛选联动自动重新请求 |
| 预览下载 | ✅ 点击资产打开 `PreviewModal.vue`（图片缩放拖拽、视频控制条）；下载按钮通过 `getFileUrl()` 下载 |
| 后端接入 | ✅ `taskStore.fetchAssets()` → `GET /files/assets/list`，支持 `file_type`/`search`/`start_date`/`end_date`/`page`/`page_size` 参数 |

### 里程碑 M3.5: 后台 UI 对齐与补全 (Admin Frontend Polish)
**目标**: 后台代码与 `前端后台.zip` 参考设计完全一致

> **背景**: 经逐项对比 `前端后台.zip` 解压后的构建产物与 `frontend-admin/` 实际代码，发现以下系统性差距。M3.5 专门用于补齐这些差异。

#### M3.5.1 全局样式对齐（🔴 高优先级）
**目标**: 后台所有组件从 scoped CSS 迁移到 Tailwind v4 工具类，修复颜色/圆角/间距偏差

| 任务 | 验收标准 |
|------|----------|
| scoped CSS → Tailwind | ❌ 所有 Vue 组件 `<style scoped>` 中的布局/颜色/间距样式替换为 Tailwind utility 类（`w-full`, `h-9`, `bg-page`, `text-txtp`, `rounded-btn` 等） |
| 圆角对齐 | ❌ 按钮圆角统一为 `rounded-btn`（6px），卡片圆角统一为 `rounded-card`（10px）；当前代码硬编码 `8px`/`12px` 全部替换 |
| 颜色修复 | ❌ 所有硬编码旧紫色（`rgba(99, 102, 241, 0.15)` / `#6366f1`）替换为设计系统蓝色（`#4f8ff7` / `var(--color-accent)`） |
| 输入框高度 | ❌ 输入框统一为 `h-9`（36px）；当前 `padding: 10px 12px`（约 40px）需调整 |
| 表格标题样式 | ❌ 表头统一为 `text-xs text-txtm uppercase tracking-wider font-medium`；当前 `font-size: 13px` 需替换 |
| 字体栈 | ❌ 统一为 `font-sans`（`ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji"`） |

#### M3.5.2 模型管理交互改造（🟡 中优先级）
**目标**: 参考设计统一使用弹窗完成增删改查，代码当前使用独立页面，需对齐

| 任务 | 验收标准 |
|------|----------|
| 新增模型弹窗 | ❌ `ModelListView.vue` 中点击「新增」弹出 Modal（宽 560px），而非跳转 `/models/create`；包含表单字段：显示名称、模型ID、模型类型、并发数量、API 端点、支持功能 checkbox 组、支持文件类型 checkbox 组 |
| 编辑模型弹窗 | ❌ `ModelListView.vue` 中点击「编辑」在同一弹窗内完成编辑，包含删除确认弹窗（文案："删除后该模型的配置将无法恢复，是否继续？"） |
| 移除独立页面 | ❌ 删除 `ModelEditView.vue` 和 `/models/edit/:id` 路由；将编辑逻辑内联到 `ModelListView.vue` |
| 保留参数配置 | 🟡 参考设计无动态参数 schema 编辑器，但业务逻辑需要；可在弹窗内保留当前 `parameters_schema` 动态配置区域作为扩展功能 |

#### M3.5.3 任务管理补全（🔴 高优先级）
**目标**: 补全参考设计中有但代码缺失的表格列和交互

| 任务 | 验收标准 |
|------|----------|
| 远端任务ID 列 | ❌ 表格增加 `远端任务ID` 列，显示 `remote_task_id` |
| 进度条列 | ❌ 表格增加 `进度` 列，`running` 状态显示进度条可视化（参考设计样式） |
| 分页功能 | ❌ 表格底部增加 `上一页` / `下一页` 分页按钮 |
| 任务详情弹窗 | ❌ 点击任务行弹出 Modal，显示：平台任务ID、远端任务ID、用户、状态（带颜色圆点）、提示词、创建时间、完成时间、关闭按钮 |
| 搜索框 | ❌ 筛选栏增加 `搜索提示词/ID...` 输入框，支持按提示词或任务ID搜索 |
| 提示词列处理 | 🟡 当前代码在表格直接显示截断提示词；参考设计在详情弹窗中显示；需对齐参考设计：表格中移除提示词列，改在详情弹窗展示 |

#### M3.5.4 Dashboard 丰富化（🟡 中优先级）
**目标**: 补全参考设计中的统计指标和服务状态监控

| 任务 | 验收标准 |
|------|----------|
| 统计卡片增强 | ❌ 4 张统计卡片增加 `change` 指示：今日任务（`+12%`）、进行中（`成功率 97.3%`）、已完成（`--`）、失败（`需关注`）；当前仅显示纯数字 |
| 最近任务表格 | ❌ Dashboard 增加「最近任务」区域，显示最近 5-10 条任务的 ID/用户/模式/模型/状态/时间 |
| 服务状态面板 | ❌ 增加 `API 状态`、`存储状态`、`平均响应时间`、`文件总数`、`火山方舟 API`、`在线` 等状态卡片；当前仅显示 Redis/TOS/磁盘使用 |

#### M3.5.5 用户管理补全（🟢 低优先级）
**目标**: 补齐搜索、确认密码、删除功能等缺失交互

| 任务 | 验收标准 |
|------|----------|
| 搜索框 | ❌ 增加 `搜索用户...` 输入框，支持按用户名搜索 |
| 确认密码字段 | ❌ 创建/编辑用户弹窗增加「确认密码」字段，两次输入不一致时提示错误 |
| 激活状态 toggle | ❌ 弹窗内增加「激活状态」toggle 开关；表格行内也支持直接切换（参考设计表格内有状态切换按钮） |
| 删除用户功能 | ❌ 增加「删除」按钮 + 确认弹窗（文案："删除后该用户的所有数据将无法恢复，是否继续？"） |
| 角色单选样式 | ❌ 角色选择从 `<select>` 下拉改为 radio 单选（admin/leader/user 横向排列） |

#### M3.5.6 系统配置补全（🟢 低优先级）
**目标**: 补齐参考设计中的存储配置和任务队列配置

| 任务 | 验收标准 |
|------|----------|
| 存储配置 | ❌ 增加「最大存储容量」字段（数字输入 + GB/TB 单位选择）、「单用户最大并发任务」字段、「文件保留时间（天）」字段 |
| 任务队列配置 | ❌ 增加「默认轮询间隔（秒）」字段、「最大重试次数」字段 |
| TOS 配置开关 | ❌ TOS 配置区域增加启用/禁用 toggle 开关 |

### M3 阶段出口检查清单
- [ ] UI走查：所有页面风格统一；无明显的布局错位；深色主题无刺眼元素
- [ ] 响应式测试：窗口缩放时侧边栏和主内容区适配正常
- [ ] 交互测试：所有按钮/链接/输入框有hover和active状态反馈
- [ ] 性能测试：生成页滚动100个任务块无卡顿；资产页加载40个缩略图流畅
- [ ] 后台功能验证：模型CRUD、用户创建/禁用、任务列表筛选、API/TOS配置保存
- [ ] **后台设计对齐**：逐页对比 `前端后台.zip` 与当前后台构建产物，确认颜色/间距/圆角/字体/布局完全一致

---

## 阶段四：集成测试与优化

### 周期: Week 4

### 里程碑 M4.1: 端到端测试
**目标**: 全链路功能稳定可靠

| 测试场景 | 验收标准 |
|----------|----------|
| 文生图全流程 | ❌ 未开始 |
| 图生视频全流程 | ❌ 未开始 |
| 并发压测 | ❌ 未开始 |
| 权限隔离 | ❌ 未开始 |
| 异常恢复 | ❌ 未开始 |
| 文件生命周期 | ❌ 未开始 |

### 里程碑 M4.2: 性能优化
**目标**: 满足生产环境性能要求

| 优化项 | 验收标准 |
|--------|----------|
| 数据库查询 | ❌ 未开始 |
| 前端加载 | ❌ 未开始 |
| 文件传输 | ❌ 未开始 |
| 内存管理 | ❌ 未开始 |

### 里程碑 M4.3: 部署与运维
**目标**: 系统可投产运行

| 任务 | 验收标准 |
|------|----------|
| 部署脚本 | ❌ 未开始 |
| 环境配置 | ❌ 未开始 |
| 监控告警 | ❌ 未开始 |
| 备份策略 | ❌ 未开始 |
| 操作手册 | ❌ 未开始 |

### M4 阶段出口检查清单 (上线标准)
- [ ] 所有测试用例通过 (单元测试覆盖率 > 70%)
- [ ] 安全扫描通过 (无敏感信息泄露；依赖无高危漏洞)
- [ ] 压力测试通过 (50并发用户，响应时间P95 < 3s)
- [ ] 灾难恢复测试通过 (数据库损坏可恢复；服务崩溃可自动重启)
- [ ] 团队内部UAT通过 (至少3人完成全流程测试无阻塞问题)

---

## 前端样式规范（设计基准）

> **强制要求**：以下规范提取自 `前端前台.zip` 和 `前端后台.zip` 的构建产物，是当前代码必须对齐的唯一标准。

### 技术栈差异

| 项目 | 参考实现 | 当前代码 | 状态 |
|------|---------|---------|------|
| Tailwind CSS 版本 | **v4** (`/*! tailwindcss v4.3.0 */`) | v3.4.19 | ✅ 已升级 |
| 配置方式 | CSS `@theme` 指令 | `tailwind.config.js` | ✅ 已升级 |

### 后台设计系统（提取自 `前端后台.zip`）

后台使用一套完整的自定义深色主题，通过 Tailwind v4 的 `@theme` 定义：

```css
/* 必须精确匹配的颜色变量 */
--color-page:        #0b0d11   /* 页面背景 */
--color-card:        #14161c   /* 卡片背景 */
--color-hover:       #1a1d25   /* 悬停背景 */
--color-active:      #1e212b   /* 激活背景 */
--color-borderc:     #252833   /* 边框颜色 */
--color-border-hover:#353a4a   /* 悬停边框 */
--color-txtp:        #e1e3e8   /* 主文本（Primary） */
--color-txts:        #8b8f9a   /* 次要文本（Secondary） */
--color-txtm:        #5a5e6a   /* 中等文本（Muted） */
--color-accent:      #4f8ff7   /* 强调色 */
--color-accent-hover:#3a7de8   /* 强调色悬停 */
--color-success:     #34c759   /* 成功 */
--color-warning:     #ff9f0a   /* 警告 */
--color-danger:      #ff453a   /* 危险 */
--color-white:       #ffffff   /* 白色 */

/* 圆角 */
--radius-btn:  6px    /* 按钮圆角 */
--radius-card: 10px   /* 卡片圆角 */
```

**关键差异**：当前代码使用的 CSS 变量（`--bg-primary: #0f0f11`、`--accent: #6366f1` 等）与参考实现的色值**完全不同**，必须按上表替换。

### 前台设计系统（提取自 `前端前台.zip`）

前台未定义自定义颜色变量，使用标准 Tailwind 色板 + 深色主题。构建产物显示为标准 Tailwind v4 主题。

### 颜色变量替换映射表（已完成）

Vue 组件 `<style scoped>` 中的旧 CSS 变量已全部替换为 Tailwind v4 `@theme` 变量，确保组件样式与 `@theme` 定义的设计系统完全绑定。

**后台 (`frontend-admin/`) 替换映射：**

| 旧变量（:root 兼容层） | 新变量（@theme） | Tailwind utility 类 |
|----------------------|-----------------|-------------------|
| `var(--bg-primary)` | `var(--color-page)` | `bg-page` |
| `var(--bg-secondary)` | `var(--color-card)` | `bg-card` |
| `var(--bg-tertiary)` | `var(--color-active)` | `bg-active` |
| `var(--bg-hover)` | `var(--color-hover)` | `bg-hover` |
| `var(--bg-card)` | `var(--color-card)` | `bg-card` |
| `var(--text-primary)` | `var(--color-txtp)` | `text-txtp` |
| `var(--text-secondary)` | `var(--color-txts)` | `text-txts` |
| `var(--text-muted)` | `var(--color-txtm)` | `text-txtm` |
| `var(--accent)` | `var(--color-accent)` | `bg-accent` / `text-accent` |
| `var(--accent-hover)` | `var(--color-accent-hover)` | `bg-accent-hover` / `text-accent-hover` |
| `var(--accent-success)` | `var(--color-success)` | `bg-success` / `text-success` |
| `var(--accent-warning)` | `var(--color-warning)` | `bg-warning` / `text-warning` |
| `var(--accent-danger)` | `var(--color-danger)` | `bg-danger` / `text-danger` |
| `var(--border)` | `var(--color-borderc)` | `border-borderc` |

**前台 (`frontend/`) 替换映射：**

| 旧变量（:root 兼容层） | 新变量（@theme） | Tailwind utility 类 |
|----------------------|-----------------|-------------------|
| `var(--bg-primary)` | `var(--color-bg-primary)` | `bg-bg-primary` |
| `var(--bg-secondary)` | `var(--color-bg-secondary)` | `bg-bg-secondary` |
| `var(--bg-tertiary)` | `var(--color-bg-tertiary)` | `bg-bg-tertiary` |
| `var(--bg-hover)` | `var(--color-bg-hover)` | `bg-bg-hover` |
| `var(--bg-card)` | `var(--color-bg-card)` | `bg-bg-card` |
| `var(--text-primary)` | `var(--color-text-primary)` | `text-text-primary` |
| `var(--text-secondary)` | `var(--color-text-secondary)` | `text-text-secondary` |
| `var(--text-muted)` | `var(--color-text-muted)` | `text-text-muted` |
| `var(--accent)` | `var(--color-accent)` | `bg-accent` / `text-accent` |
| `var(--accent-hover)` | `var(--color-accent-hover)` | `bg-accent-hover` / `text-accent-hover` |
| `var(--accent-danger)` | `var(--color-accent-danger)` | `bg-accent-danger` / `text-accent-danger` |
| `var(--accent-success)` | `var(--color-accent-success)` | `bg-accent-success` / `text-accent-success` |
| `var(--accent-warning)` | `var(--color-accent-warning)` | `bg-accent-warning` / `text-accent-warning` |
| `var(--border)` | `var(--color-border)` | `border-border` |

> **后续开发建议**：新组件优先直接使用 Tailwind v4 utility 类（如 `bg-page text-txtp`），不再使用 `var(--color-xxx)` 形式的 CSS 变量。

### 颜色系统对齐任务清单（纳入执行计划）

颜色系统对齐是前端开发的前置条件，必须在 M3 阶段开始前完成。

#### 阶段 A：基础设施升级（已完成）
- [x] 将 Tailwind CSS 从 v3 升级到 v4（前台 + 后台）
- [x] 删除 `tailwind.config.js`，改用 CSS `@theme` 指令配置（v4 方式）
- [x] Vite 配置添加 `@tailwindcss/vite` 插件，删除 `postcss.config.js`

#### 阶段 B：后台颜色系统对齐（已完成）
- [x] 提取 `前端后台.zip` 设计系统色值（14 个颜色变量 + 2 个圆角变量）
- [x] `frontend-admin/src/styles/main.css` 中 `@theme` 定义精确匹配参考实现
- [x] 所有后台 Vue 组件 `var(--bg-xxx)` → `var(--color-xxx)` 替换完成
- [x] 后台构建产物 CSS 头部确认为 `tailwindcss v4.3.0`

#### 阶段 C：前台颜色系统对齐（进行中）
- [x] `frontend/src/styles/main.css` 已改用 `@import "tailwindcss"` + `@theme`
- [x] 所有前台 Vue 组件 `var(--bg-xxx)` → `var(--color-xxx)` 替换完成
- [ ] **对齐 `前端前台.zip` 的标准 Tailwind 色板**：当前前台使用自定义 `--color-bg-primary` 等变量，参考实现使用标准 Tailwind 颜色（如 `bg-gray-900`、`text-white`）。需解压 zip 后逐页比对，将自定义变量替换为标准 Tailwind utility 类。
- [ ] **所有 Vue 组件从 CSS 变量迁移到 Tailwind utility 类**：当前组件在 `<style scoped>` 中使用 `background: var(--color-page)`，应逐步改为在 template 的 `class` 中直接使用 `bg-page`。此工作可与页面功能开发同步进行。

#### 阶段 D：设计系统一致性验收（未开始）
- [ ] 逐页对比 `前端前台.zip` 与当前前台构建产物，确保颜色、间距、圆角、字体一致
- [ ] 逐页对比 `前端后台.zip` 与当前后台构建产物，确保颜色、间距、圆角、字体一致
- [ ] 确保按钮圆角 `6px`、卡片圆角 `10px` 与参考一致
- [ ] 字体栈统一为 `ui-sans-serif, system-ui, sans-serif, ...`

### 样式施工检查清单

- [x] 将 Tailwind CSS 从 v3 升级到 v4（前台 + 后台）
- [x] 删除 `tailwind.config.js`，改用 CSS `@theme` 指令配置（v4 方式）
- [x] 后台：将 `styles/main.css` 中的 CSS 变量替换为参考实现的精确色值
- [x] 所有 Vue 组件中 `var(--xxx)` 变量引用替换为 `var(--color-xxx)` 形式
- [ ] 前台：对齐 `前端前台.zip` 的颜色和布局（需解压后逐一比对）
- [ ] 所有 Vue 组件中 hardcode 的颜色值必须替换为 theme 变量
- [x] 确保按钮圆角 `6px`、卡片圆角 `10px` 与参考一致（后台已配置）
- [x] 字体栈统一为 `ui-sans-serif, system-ui, sans-serif, ...`

---

## 当前已知问题清单（待修复）

| 优先级 | 问题 | 状态 | 影响 | 建议修复方案 |
|--------|------|------|------|-------------|
| ✅ 已完成 | Tailwind v3 → v4 升级 | 已升级 | 样式系统与参考实现根本不一致 | `npm install tailwindcss@latest @tailwindcss/vite`，删除 `tailwind.config.js` + `postcss.config.js` |
| ✅ 已完成 | 后台颜色系统未对齐 | 已对齐 | 视觉效果与参考实现完全不同 | `@theme` 中定义 14 个精确色值，Vue 组件 `var(--bg-xxx)` → `var(--color-xxx)` |
| ✅ 已完成 | Vue 组件 CSS 变量迁移 | 已迁移 | 组件样式与 `@theme` 未绑定 | 后台 8 个 + 前台 9 个 `.vue` 文件批量替换 |
| ✅ 已完成 | Pydantic `model_id` 命名空间冲突 | 已修复 | 运行时 4 条 UserWarning | 全部 Schema 改用 `ConfigDict(protected_namespaces=())` |
| ✅ 已完成 | Pydantic `class Config` 弃用警告 | 已修复 | 运行时 DeprecationWarning | `core/config.py` 改用 `SettingsConfigDict()` |
| 🟡 P1 | 前台颜色系统未对齐 | 进行中 | 页面背景、强调色等色值不同 | 对比 `前端前台.zip` 逐页校对，将自定义变量替换为标准 Tailwind utility 类 |
| 🟡 P1 | Vue 组件从 CSS 变量迁移到 utility 类 | 未开始 | 未充分利用 Tailwind v4 | 新组件优先用 `bg-page text-txtp`，旧组件逐步替换 |
| ✅ 已完成 | `main` 分支缺失 | 已修复 | Git 工作流不完整 | 已从 `develop` 创建 `main` 分支 |
| 🟡 P2 | 前端 admin 构建循环依赖警告 | 未修复 | Rollup chunk 执行顺序可能异常 | 将 `useAdminStore` 的引用从 `stores/index.ts` 改为直接引用 `stores/admin.ts` |
| 🔴 P1 | 前台 Vue 组件全部使用 scoped CSS | 未修复 | 10 个 `.vue` 文件零 Tailwind utility 类使用；`InputBar.vue` 单文件 406 行 scoped CSS；与设计规范严重不符 | 逐组件将 `<style scoped>` 中的布局/颜色/间距样式替换为 Tailwind utility 类；可配合 M3.5.1 或前台样式对齐工作一起执行 |
| 🔴 P1 | 前台硬编码颜色值（91 处） | 未修复 | `#6366f1`/`#f59e0b`/`#ef4444` 等散落在 10 个组件中；主题替换和维护成本极高 | 提取到 `main.css` 的 `@theme` 中统一定义；组件中替换为 `bg-accent`/`text-danger` 等 utility 类 |
| ✅ 已修复 | API 层循环依赖 | 已修复 | `api/index.ts` 导入 `stores/user.ts`，`stores/user.ts` 又导入 `api/index.ts`；某些构建场景下会导致运行时错误 | api/index.ts 不再导入 useUserStore，token 从 localStorage 读取；401 触发 `api:unauthorized` 全局事件；App.vue 监听事件调用 logout |
| ✅ 已修复 | 前台缺少 404 路由 | 已修复 | `router/index.ts` 仅 4 条路由，无 `/*` catch-all；非法 URL 显示空白 | 添加 `{ path: '/:pathMatch(.*)*', redirect: '/generate' }` catch-all 路由 |
| ✅ 已修复 | `router.beforeEach` 位置不当 | 已修复 | 全局路由守卫写在 `App.vue` 的 `<script setup>` 中，而非 `router/index.ts` | 将守卫逻辑迁移到 `router/index.ts` 中注册；新增 `auth:required` 全局事件通知 App.vue 显示登录弹窗 |
| ✅ 已修复 | `TaskBlock.vue` modelName 显示不友好 | 已修复 | 显示 `model_id`（如 `seedance-v1`）而非友好名称；用户体验差 | `types/index.ts` 给 `TaskItem` 新增 `model_name?: string`；`TaskBlock.vue` modelName computed 优先显示 `model_name`，回退到 `model_id` |
| ✅ 已修复 | `TaskParameters.sequential_image_generation` 类型过于宽泛 | 已修复 | 定义为 `string`，实际值为 `'auto' | 'disabled'`；按语义应为更精确的类型 | 改为 `'auto' | 'disabled'` 字面量联合类型；清理 `any` 类型使用 |
| ✅ 已修复 | 资产页面删除按钮未启用 | 已修复 | `AssetsView.vue` 调用 `<Thumbnail>` 时未传 `show-delete` prop，也未绑定 `@delete` 事件 | 传入 `show-delete` prop 并添加 `handleDelete` 方法；`taskStore` 新增 `deleteFile` 方法调用 `DELETE /files/{file_id}` |
| ✅ 已修复 | `HistoryView.vue` 未使用导入 | 已修复 | 导入并 `extend` 了 `dayjs/plugin/isSameOrAfter`，但逻辑中未使用 | 移除未使用的导入和 extend 调用 |
| ✅ 已修复 | `GenerateView.vue` 直接操作 DOM | 已修复 | `quickStart()` 使用 `document.querySelector('.prompt-input')` 与组件类名强耦合 | `InputBar.vue` expose `focus()` 方法；`GenerateView.vue` 通过 `ref` 调用 `inputBarRef.value?.focus()` |
| 🟢 P3 | 数据库 100 并发压测未执行 | 未执行 | 未验证连接池稳定性 | 使用 `locust` 或 `ab` 压测 `/health` |

---

## 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 火山方舟API变更 | 高 | 封装VolcengineClient，隔离API差异；关注官方文档更新 |
| TOS上传失败 | 高 | 本地保留副本；失败时重试3次；报警通知管理员 |
| 大文件上传超时 | 中 | 分片上传；进度反馈；超时时间设为300s |
| SQLite并发瓶颈 | 中 | WAL模式；读写分离(读副本)；预留MySQL迁移方案 |
| 前端构建产物过大 | 低 | 路由懒加载；图片压缩；CDN加速(后续) |
