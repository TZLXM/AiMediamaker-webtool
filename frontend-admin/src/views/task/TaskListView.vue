<template>
  <div class="max-w-[1400px]">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-xl font-semibold">任务管理</h1>
      <div class="flex items-center gap-3">
        <select v-model="filterMode" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-[13px] outline-none">
          <option value="">全部模式</option>
          <option value="image">图片</option>
          <option value="video">视频</option>
        </select>
        <select v-model="filterStatus" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-[13px] outline-none">
          <option value="">全部状态</option>
          <option value="running">进行中</option>
          <option value="queued">排队中</option>
          <option value="succeeded">已完成</option>
          <option value="failed">失败</option>
        </select>
        <button class="flex items-center gap-1 px-3 h-9 bg-transparent border-none text-txts text-[13px] cursor-pointer" @click="fetchTasks">
          <RefreshIcon :size="14" /> 刷新
        </button>
      </div>
    </div>
    <div class="bg-card border border-borderc rounded-card overflow-hidden">
      <table class="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">平台任务ID</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">用户</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">模式</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">模型</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">提示词</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">状态</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">创建时间</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in filteredTasks" :key="task.id">
            <td class="px-4 py-3 border-t border-borderc font-mono text-xs text-txts">{{ task.platform_task_id }}</td>
            <td class="px-4 py-3 border-t border-borderc">{{ task.username }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <span class="px-2 py-0.5 rounded text-xs font-medium" :class="task.mode === 'image' ? 'bg-accent/15 text-accent' : 'bg-warning/15 text-warning'">{{ task.mode === 'image' ? '图片' : '视频' }}</span>
            </td>
            <td class="px-4 py-3 border-t border-borderc font-mono text-xs text-txts">{{ task.model_id }}</td>
            <td class="px-4 py-3 border-t border-borderc max-w-[200px] truncate">{{ task.prompt }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <span class="px-2 py-0.5 rounded text-xs" :class="statusClass(task.status)">{{ statusLabel(task.status) }}</span>
            </td>
            <td class="px-4 py-3 border-t border-borderc">{{ formatDate(task.created_at) }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <button v-if="['pending','queued','running'].includes(task.status)" class="px-2 py-1 bg-transparent border-none text-danger text-[13px] cursor-pointer" @click="cancelTask(task)">
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
import api from '@/api'
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
  try {
    const params: Record<string, any> = {}
    if (filterMode.value) params.mode = filterMode.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await api.get('/admin/tasks', { params })
    tasks.value = res.data
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取任务列表失败')
  }
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '等待中', queued: '排队中', running: '进行中',
    succeeded: '已完成', failed: '失败', cancelled: '已取消',
  }
  return map[status] || status
}

function statusClass(status: string) {
  const map: Record<string, string> = {
    pending: 'bg-txtm/15 text-txtm',
    queued: 'bg-warning/15 text-warning',
    running: 'bg-accent/15 text-accent',
    succeeded: 'bg-success/15 text-success',
    failed: 'bg-danger/15 text-danger',
    cancelled: 'bg-txtm/15 text-txtm',
  }
  return map[status] || ''
}

function formatDate(d: string) {
  return dayjs(d).format('MM-DD HH:mm')
}

async function cancelTask(task: AdminTask) {
  if (!confirm('确定要取消该任务吗？')) return
  try {
    await api.post(`/admin/tasks/${task.platform_task_id}/cancel`)
    await fetchTasks()
  } catch (e: any) {
    alert(e.response?.data?.detail || '取消失败')
  }
}

onMounted(fetchTasks)
</script>
