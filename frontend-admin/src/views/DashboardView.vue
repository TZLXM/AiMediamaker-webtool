<template>
  <div class="dashboard-page">
    <h1 class="text-xl font-semibold mb-6">系统状态</h1>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-4 gap-4 mb-8">
      <div class="bg-card border border-borderc rounded-card p-5 flex items-center gap-4">
        <div class="w-12 h-12 rounded-card flex items-center justify-center bg-accent/15 text-accent">
          <ActivityIcon :size="24" />
        </div>
        <div class="flex flex-col">
          <span class="text-2xl font-semibold">{{ stats.today_tasks }}</span>
          <div class="flex items-center gap-1.5 mt-0.5">
            <span class="text-[13px] text-txts">今日任务</span>
            <span class="text-[11px] text-success font-medium">+12%</span>
          </div>
        </div>
      </div>
      <div class="bg-card border border-borderc rounded-card p-5 flex items-center gap-4">
        <div class="w-12 h-12 rounded-card flex items-center justify-center bg-warning/15 text-warning">
          <ClockIcon :size="24" />
        </div>
        <div class="flex flex-col">
          <span class="text-2xl font-semibold">{{ stats.active_tasks }}</span>
          <div class="flex items-center gap-1.5 mt-0.5">
            <span class="text-[13px] text-txts">进行中</span>
            <span class="text-[11px] text-txts">成功率 {{ stats.success_rate }}%</span>
          </div>
        </div>
      </div>
      <div class="bg-card border border-borderc rounded-card p-5 flex items-center gap-4">
        <div class="w-12 h-12 rounded-card flex items-center justify-center bg-success/15 text-success">
          <CheckCircleIcon :size="24" />
        </div>
        <div class="flex flex-col">
          <span class="text-2xl font-semibold">{{ stats.completed_tasks }}</span>
          <div class="flex items-center gap-1.5 mt-0.5">
            <span class="text-[13px] text-txts">已完成</span>
            <span class="text-[11px] text-txtm">--</span>
          </div>
        </div>
      </div>
      <div class="bg-card border border-borderc rounded-card p-5 flex items-center gap-4">
        <div class="w-12 h-12 rounded-card flex items-center justify-center bg-danger/15 text-danger">
          <AlertTriangleIcon :size="24" />
        </div>
        <div class="flex flex-col">
          <span class="text-2xl font-semibold">{{ stats.failed_tasks }}</span>
          <div class="flex items-center gap-1.5 mt-0.5">
            <span class="text-[13px] text-txts">失败</span>
            <span class="text-[11px] text-danger font-medium">需关注</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 服务状态面板 -->
    <div class="grid grid-cols-3 gap-4 mb-8">
      <div class="bg-card border border-borderc rounded-card p-5">
        <h2 class="text-base font-semibold mb-4">服务状态</h2>
        <div class="flex flex-col gap-3">
          <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <span class="text-sm text-txts">API 状态</span>
            <span class="px-2.5 py-1 rounded text-xs font-medium" :class="stats.api_status === 'online' ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'">
              {{ stats.api_status === 'online' ? '在线' : '离线' }}
            </span>
          </div>
          <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <span class="text-sm text-txts">存储状态</span>
            <span class="px-2.5 py-1 rounded text-xs font-medium" :class="stats.disk_usage < 90 ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'">
              {{ stats.disk_usage < 90 ? '正常' : '告警' }}
            </span>
          </div>
          <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <span class="text-sm text-txts">Redis 连接</span>
            <span class="px-2.5 py-1 rounded text-xs font-medium" :class="stats.redis_connected ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'">
              {{ stats.redis_connected ? '正常' : '异常' }}
            </span>
          </div>
        </div>
      </div>

      <div class="bg-card border border-borderc rounded-card p-5">
        <h2 class="text-base font-semibold mb-4">系统指标</h2>
        <div class="flex flex-col gap-3">
          <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <span class="text-sm text-txts">平均响应时间</span>
            <span class="text-sm font-medium">{{ stats.avg_response_time }}s</span>
          </div>
          <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <span class="text-sm text-txts">文件总数</span>
            <span class="text-sm font-medium">{{ stats.total_files }}</span>
          </div>
          <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <span class="text-sm text-txts">磁盘使用</span>
            <span class="text-sm font-medium">{{ stats.disk_usage }}%</span>
          </div>
        </div>
      </div>

      <div class="bg-card border border-borderc rounded-card p-5">
        <h2 class="text-base font-semibold mb-4">平台连接</h2>
        <div class="flex flex-col gap-3">
          <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <span class="text-sm text-txts">火山方舟 API</span>
            <span class="px-2.5 py-1 rounded text-xs font-medium" :class="stats.volcengine_status === 'online' ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'">
              {{ stats.volcengine_status === 'online' ? '在线' : '离线' }}
            </span>
          </div>
          <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <span class="text-sm text-txts">TOS 连接</span>
            <span class="px-2.5 py-1 rounded text-xs font-medium" :class="stats.tos_connected ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'">
              {{ stats.tos_connected ? '正常' : '异常' }}
            </span>
          </div>
          <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <span class="text-sm text-txts">总用户数</span>
            <span class="text-sm font-medium">{{ stats.total_users }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近任务 -->
    <div class="bg-card border border-borderc rounded-card p-5">
      <h2 class="text-base font-semibold mb-4">最近任务</h2>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-borderc">
              <th class="text-left py-2.5 px-3 text-xs text-txtm uppercase tracking-wider font-medium">平台任务ID</th>
              <th class="text-left py-2.5 px-3 text-xs text-txtm uppercase tracking-wider font-medium">用户</th>
              <th class="text-left py-2.5 px-3 text-xs text-txtm uppercase tracking-wider font-medium">模式</th>
              <th class="text-left py-2.5 px-3 text-xs text-txtm uppercase tracking-wider font-medium">模型</th>
              <th class="text-left py-2.5 px-3 text-xs text-txtm uppercase tracking-wider font-medium">状态</th>
              <th class="text-left py-2.5 px-3 text-xs text-txtm uppercase tracking-wider font-medium">创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in stats.recent_tasks" :key="task.platform_task_id" class="border-b border-borderc/50 hover:bg-hover transition-colors">
              <td class="py-3 px-3 font-mono text-txts">{{ task.platform_task_id }}</td>
              <td class="py-3 px-3 text-txtp">{{ task.username }}</td>
              <td class="py-3 px-3">
                <span class="px-2 py-0.5 rounded text-xs font-medium" :class="task.mode === 'video' ? 'bg-accent/15 text-accent' : 'bg-success/15 text-success'">
                  {{ task.mode === 'video' ? '视频' : '图片' }}
                </span>
              </td>
              <td class="py-3 px-3 text-txts">{{ task.model_id }}</td>
              <td class="py-3 px-3">
                <span class="px-2 py-0.5 rounded text-xs font-medium" :class="statusClass(task.status)">
                  {{ statusLabel(task.status) }}
                </span>
              </td>
              <td class="py-3 px-3 text-txts">{{ formatTime(task.created_at) }}</td>
            </tr>
            <tr v-if="!stats.recent_tasks?.length">
              <td colspan="6" class="py-8 text-center text-txtm">暂无任务</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Activity, Clock, CheckCircle, AlertTriangle } from 'lucide-vue-next'
import api from '@/api'
import type { SystemStatus } from '@/types'

const ActivityIcon = Activity
const ClockIcon = Clock
const CheckCircleIcon = CheckCircle
const AlertTriangleIcon = AlertTriangle

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
  redis_connected: false,
  tos_connected: false,
  api_status: 'offline',
  volcengine_status: 'offline',
  recent_tasks: [],
})

function statusClass(status: string): string {
  switch (status) {
    case 'succeeded':
      return 'bg-success/15 text-success'
    case 'failed':
      return 'bg-danger/15 text-danger'
    case 'running':
      return 'bg-accent/15 text-accent'
    case 'queued':
      return 'bg-warning/15 text-warning'
    case 'cancelled':
      return 'bg-txtm/15 text-txtm'
    default:
      return 'bg-txtm/15 text-txtm'
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
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function fetchStatus() {
  try {
    const res = await api.get('/admin/status')
    stats.value = res.data
  } catch (e: any) {
    // silent fail
  }
}

onMounted(fetchStatus)
</script>
