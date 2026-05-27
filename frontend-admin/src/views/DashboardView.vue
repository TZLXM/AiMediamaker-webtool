<template>
  <div class="space-y-6">
    <!-- 顶部标题栏 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-txtp">仪表盘</h1>
        <p class="text-xs text-txtm mt-1">首页 / 仪表盘</p>
      </div>
      <div class="flex items-center gap-3">
        <span class="font-mono text-xs text-txtm">{{ currentTime }}</span>
        <button
          class="flex items-center gap-2 px-4 py-2 rounded-btn border border-borderc text-sm text-txtp hover:border-accent hover:text-accent transition-all duration-200"
          @click="fetchStatus"
        >
          <RefreshCwIcon :size="16" />
          <span>刷新</span>
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-4 gap-4">
      <div
        v-for="(card, idx) in statCards"
        :key="idx"
        class="bg-card border border-borderc rounded-card p-5 hover:border-border-hover transition-all duration-200"
      >
        <p class="text-xs text-txtm uppercase tracking-wider mb-3">{{ card.label }}</p>
        <p class="text-[28px] font-bold text-txtp tracking-tight" :class="card.color">{{ card.value }}</p>
        <div class="flex items-center gap-1 mt-2">
          <component
            :is="card.up ? ArrowUpIcon : ArrowDownIcon"
            :size="12"
            :class="card.up ? 'text-success' : 'text-danger'"
          />
          <span class="text-xs" :class="card.up ? 'text-success' : 'text-danger'">{{ card.change }}</span>
        </div>
      </div>
    </div>

    <!-- 最近任务表格 -->
    <div class="bg-card border border-borderc rounded-card">
      <div class="flex items-center justify-between px-5 py-4 border-b border-borderc">
        <h2 class="text-sm font-semibold text-txtp">最近任务</h2>
        <RouterLink to="/tasks" class="text-xs text-accent hover:underline">
          查看全部 →
        </RouterLink>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-borderc">
              <th class="text-left text-xs text-txtm uppercase tracking-wider px-5 py-3 font-medium">任务ID</th>
              <th class="text-left text-xs text-txtm uppercase tracking-wider px-4 py-3 font-medium">用户</th>
              <th class="text-left text-xs text-txtm uppercase tracking-wider px-4 py-3 font-medium">模式</th>
              <th class="text-left text-xs text-txtm uppercase tracking-wider px-4 py-3 font-medium">模型</th>
              <th class="text-left text-xs text-txtm uppercase tracking-wider px-4 py-3 font-medium">状态</th>
              <th class="text-left text-xs text-txtm uppercase tracking-wider px-4 py-3 font-medium">时间</th>
              <th class="text-left text-xs text-txtm uppercase tracking-wider px-4 py-3 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="task in stats.recent_tasks"
              :key="task.platform_task_id"
              class="border-b border-borderc/50 hover:bg-hover transition-colors duration-150"
            >
              <td class="px-5 py-3 font-mono text-xs text-accent">{{ task.platform_task_id }}</td>
              <td class="px-4 py-3 text-sm text-txts">{{ task.username }}</td>
              <td class="px-4 py-3">
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                  :class="task.mode === 'video' ? 'bg-accent/10 text-accent' : 'bg-success/10 text-success'"
                >
                  {{ task.mode === 'video' ? '视频生成' : '图片生成' }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-txts">{{ task.model_id }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full" :class="statusDot(task.status)" />
                  <span class="text-xs" :class="statusColor(task.status)">{{ statusLabel(task.status) }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-xs text-txtm font-mono">{{ formatTime(task.created_at) }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1">
                  <button class="p-1.5 rounded text-txts hover:text-txtp hover:bg-hover transition-colors">
                    <EyeIcon :size="14" />
                  </button>
                  <button class="p-1.5 rounded text-txts hover:text-danger hover:bg-hover transition-colors">
                    <XIcon :size="14" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!stats.recent_tasks?.length">
              <td colspan="7" class="py-8 text-center text-txtm">暂无任务</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 底部两列卡片 -->
    <div class="grid grid-cols-2 gap-4">
      <!-- API 状态 -->
      <div class="bg-card border border-borderc rounded-card p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-txtp">API 状态</h3>
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-success animate-pulse" />
            <span class="text-xs text-success">在线</span>
          </div>
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs text-txts">火山方舟 API</span>
            <span
              class="text-xs font-medium"
              :class="stats.volcengine_status === 'online' ? 'text-success' : 'text-danger'"
            >
              {{ stats.volcengine_status === 'online' ? '已连接' : '未连接' }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-txts">平均响应时间</span>
            <span class="text-xs text-txtp font-medium font-mono">{{ stats.avg_response_time }}s</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-txts">今日请求数</span>
            <span class="text-xs text-txtp font-medium font-mono">{{ stats.today_tasks }}</span>
          </div>
        </div>
      </div>

      <!-- 存储状态 -->
      <div class="bg-card border border-borderc rounded-card p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-txtp">存储状态</h3>
          <span class="text-xs text-txts font-mono">{{ formatBytes(stats.disk_used) }} / {{ formatBytes(stats.disk_total) }}</span>
        </div>
        <div class="w-full h-2 bg-page rounded-full overflow-hidden mb-3">
          <div
            class="h-full rounded-full"
            :style="{ width: stats.disk_total ? `${(stats.disk_used / stats.disk_total) * 100}%` : '0%' }"
          />
        </div>
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs text-txts">已用空间</span>
            <span class="text-xs text-txtp font-medium font-mono">{{ formatBytes(stats.disk_used) }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-txts">剩余空间</span>
            <span class="text-xs text-txtp font-medium font-mono">{{ formatBytes(stats.disk_free) }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-txts">文件总数</span>
            <span class="text-xs text-txtp font-medium font-mono">{{ stats.total_files.toLocaleString() }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RefreshCw, ArrowUp, ArrowDown, Eye, X } from 'lucide-vue-next'
import api from '@/api'
import type { SystemStatus } from '@/types'

const RefreshCwIcon = RefreshCw
const ArrowUpIcon = ArrowUp
const ArrowDownIcon = ArrowDown
const EyeIcon = Eye
const XIcon = X

const stats = ref<SystemStatus>({
  active_tasks: 0,
  queued_tasks: 0,
  total_users: 0,
  total_tasks: 0,
  today_tasks: 0,
  completed_tasks: 0,
  failed_tasks: 0,
  success_rate: 0,
  total_files: 0,
  avg_response_time: 0,
  disk_usage: 0,
  disk_total: 0,
  disk_used: 0,
  disk_free: 0,
  redis_connected: false,
  tos_connected: false,
  api_status: 'offline',
  volcengine_status: 'offline',
  recent_tasks: [],
})

const statCards = computed(() => [
  { label: '今日任务', value: String(stats.value.today_tasks), change: '+12%', up: true, color: 'text-accent' },
  { label: '进行中', value: String(stats.value.active_tasks), change: '队列深度', up: true, color: 'text-warning' },
  { label: '已完成', value: String(stats.value.completed_tasks), change: `成功率 ${stats.value.success_rate}%`, up: true, color: 'text-success' },
  { label: '失败', value: String(stats.value.failed_tasks), change: '需关注', up: false, color: 'text-danger' },
])

const currentTime = ref('')
let timer: ReturnType<typeof setInterval> | null = null

function updateTime() {
  currentTime.value = new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

function statusDot(status: string): string {
  switch (status) {
    case 'succeeded':
      return 'bg-success'
    case 'failed':
      return 'bg-danger'
    case 'running':
      return 'bg-accent'
    case 'queued':
      return 'bg-warning'
    default:
      return 'bg-txtm'
  }
}

function statusColor(status: string): string {
  switch (status) {
    case 'succeeded':
      return 'text-success'
    case 'failed':
      return 'text-danger'
    case 'running':
      return 'text-accent'
    case 'queued':
      return 'text-warning'
    default:
      return 'text-txtm'
  }
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    pending: '等待中',
    queued: '排队中',
    running: '运行中',
    succeeded: '已完成',
    failed: '失败',
    cancelled: '已取消',
    cancelling: '取消中',
    downloading: '下载中',
  }
  return map[status] || status
}

function formatTime(iso: string): string {
  if (!iso) return '--'
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function formatBytes(bytes: number): string {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(1)} ${units[i]}`
}

async function fetchStatus() {
  try {
    const res = await api.get('/admin/status')
    stats.value = res.data
  } catch (e: any) {
    // silent fail
  }
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  fetchStatus()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
