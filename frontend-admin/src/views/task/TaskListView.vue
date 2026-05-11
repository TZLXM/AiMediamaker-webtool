<template>
  <div class="page-container">
    <div class="page-header">
      <h1>任务管理</h1>
      <div class="filter-bar">
        <select v-model="filterMode">
          <option value="">全部模式</option>
          <option value="image">图片</option>
          <option value="video">视频</option>
        </select>
        <select v-model="filterStatus">
          <option value="">全部状态</option>
          <option value="running">进行中</option>
          <option value="queued">排队中</option>
          <option value="succeeded">已完成</option>
          <option value="failed">失败</option>
        </select>
        <button class="btn-text" @click="fetchTasks">
          <RefreshIcon :size="14" /> 刷新
        </button>
      </div>
    </div>
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>平台任务ID</th>
            <th>用户</th>
            <th>模式</th>
            <th>模型</th>
            <th>提示词</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in filteredTasks" :key="task.id">
            <td class="mono">{{ task.platform_task_id }}</td>
            <td>{{ task.username }}</td>
            <td>
              <span class="tag" :class="task.mode">{{ task.mode === 'image' ? '图片' : '视频' }}</span>
            </td>
            <td class="mono">{{ task.model_id }}</td>
            <td class="truncate">{{ task.prompt }}</td>
            <td>
              <span class="status-dot" :class="task.status">{{ statusLabel(task.status) }}</span>
            </td>
            <td>{{ formatDate(task.created_at) }}</td>
            <td>
              <button v-if="['pending','queued','running'].includes(task.status)" class="btn-text danger" @click="cancelTask(task)">
                取消
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import dayjs from 'dayjs'
// import api from '@/api'
import type { AdminTask } from '@/types'

const RefreshIcon = RefreshCw

const tasks = ref<AdminTask[]>([])
const filterMode = ref('')
const filterStatus = ref('')

const filteredTasks = computed(() => {
  return tasks.value.filter((t) => {
    if (filterMode.value && t.mode !== filterMode.value) return false
    if (filterStatus.value && t.status !== filterStatus.value) return false
    return true
  })
})

async function fetchTasks() {
  // TODO: 接入管理端任务列表API
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '等待中', queued: '排队中', running: '进行中',
    succeeded: '已完成', failed: '失败', cancelled: '已取消',
  }
  return map[status] || status
}

function formatDate(d: string) {
  return dayjs(d).format('MM-DD HH:mm')
}

async function cancelTask(_task: AdminTask) {
  if (!confirm('确定要取消该任务吗？')) return
  // TODO: 接入取消任务API
}

onMounted(fetchTasks)
</script>

<style scoped>
.page-container { max-width: 1400px; }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 24px;
}
.page-header h1 { font-size: 20px; font-weight: 600; }

.filter-bar {
  display: flex; align-items: center; gap: 12px;
}
.filter-bar select {
  padding: 8px 12px; background: var(--bg-secondary);
  border: 1px solid var(--border); border-radius: 8px;
  color: var(--text-primary); font-size: 13px; outline: none;
}
.btn-text {
  display: flex; align-items: center; gap: 4px;
  padding: 8px 12px; background: transparent; border: none;
  color: var(--text-secondary); font-size: 13px; cursor: pointer;
}

.table-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}
.data-table {
  width: 100%; border-collapse: collapse; font-size: 14px;
}
.data-table th {
  text-align: left; padding: 12px 16px;
  background: var(--bg-tertiary); color: var(--text-secondary);
  font-weight: 500; font-size: 13px;
}
.data-table td {
  padding: 12px 16px; border-top: 1px solid var(--border);
}
.mono { font-family: monospace; font-size: 12px; color: var(--text-secondary); }
.truncate {
  max-width: 200px; white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis;
}

.tag {
  padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500;
}
.tag.image { background: rgba(99, 102, 241, 0.15); color: var(--accent); }
.tag.video { background: rgba(245, 158, 11, 0.15); color: var(--accent-warning); }

.status-dot {
  padding: 2px 8px; border-radius: 4px; font-size: 12px;
}
.status-dot.pending { background: rgba(113, 113, 122, 0.15); color: var(--text-muted); }
.status-dot.queued { background: rgba(245, 158, 11, 0.15); color: var(--accent-warning); }
.status-dot.running { background: rgba(99, 102, 241, 0.15); color: var(--accent); }
.status-dot.succeeded { background: rgba(34, 197, 94, 0.15); color: var(--accent-success); }
.status-dot.failed { background: rgba(239, 68, 68, 0.15); color: var(--accent-danger); }
.status-dot.cancelled { background: rgba(113, 113, 122, 0.15); color: var(--text-muted); }

.data-table .btn-text {
  padding: 4px 8px; background: transparent; border: none;
  color: var(--accent); font-size: 13px; cursor: pointer;
}
.data-table .btn-text.danger { color: var(--accent-danger); }
</style>
