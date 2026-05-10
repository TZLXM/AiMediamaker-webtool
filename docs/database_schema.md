# 数据库表结构设计

## 1. users (用户表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| username | VARCHAR(64) UNIQUE | 用户名 |
| password_hash | VARCHAR(255) | bcrypt哈希密码 |
| role | VARCHAR(16) | admin/leader/user |
| is_active | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 2. tasks (任务表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| platform_task_id | VARCHAR(64) UNIQUE | 平台任务ID |
| user_id | INTEGER FK | 关联用户 |
| mode | VARCHAR(16) | image/video |
| model_id | VARCHAR(64) | 模型ID |
| prompt | TEXT | 提示词 |
| parameters | JSON | 生成参数 |
| remote_task_id | VARCHAR(128) | 远端API任务ID |
| status | VARCHAR(16) | 任务状态 |
| error_code | VARCHAR(64) | 错误码 |
| error_message | TEXT | 错误信息 |
| started_at | DATETIME | 开始时间 |
| completed_at | DATETIME | 完成时间 |
| cancelled_at | DATETIME | 取消时间 |
| usage_tokens | INTEGER | Token用量 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 3. files (文件表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| file_id | VARCHAR(64) UNIQUE | 文件唯一ID |
| original_name | VARCHAR(255) | 原始文件名 |
| storage_name | VARCHAR(255) | 存储文件名 |
| storage_path | VARCHAR(512) | 本地存储路径 |
| file_type | VARCHAR(16) | image/video/audio |
| mime_type | VARCHAR(128) | MIME类型 |
| size_bytes | INTEGER | 文件大小 |
| source | VARCHAR(16) | upload/output/base64 |
| task_id | INTEGER FK | 关联输入任务 |
| source_task_id | INTEGER FK | 关联输出任务 |
| public_url | TEXT | TOS公网URL |
| storage_status | VARCHAR(16) | local/uploading/uploaded/failed |
| user_id | INTEGER | 上传者ID |
| meta_info | JSON | 额外元数据 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 4. api_configs (API配置表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| name | VARCHAR(64) | 配置名称 |
| platform | VARCHAR(32) | 平台类型 |
| api_key | TEXT | API密钥 |
| base_url | VARCHAR(255) | API基础URL |
| total_concurrency | INTEGER | 总并发限制 |
| is_active | BOOLEAN | 是否启用 |
| extra_config | JSON | 额外配置 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 5. model_configs (模型配置表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| name | VARCHAR(64) | 显示名称 |
| model_id | VARCHAR(64) UNIQUE | 模型ID |
| api_config_id | INTEGER | 关联API配置 |
| mode | VARCHAR(16) | image/video |
| description | TEXT | 描述 |
| concurrency_limit | INTEGER | 并发限制 |
| parameters_schema | JSON | 参数Schema |
| supported_input_types | JSON | 支持输入类型 |
| is_active | BOOLEAN | 是否启用 |
| sort_order | INTEGER | 排序权重 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
