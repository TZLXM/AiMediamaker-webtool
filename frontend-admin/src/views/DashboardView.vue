<template>
  <div class="dashboard-page">
    <h1 class="text-xl font-semibold mb-6">系统状态</h1>
    <div class="grid grid-cols-4 gap-4 mb-8">
      <div class="bg-card border border-borderc rounded-card p-5 flex items-center gap-4">
        <div class="w-12 h-12 rounded-card flex items-center justify-center bg-accent/15 text-accent">
          <ActivityIcon :size="24" />
        </div>
        <div class="flex flex-col">
          <span class="text-2xl font-semibold">{{ stats.active_tasks }}</span>
          <span class="text-[13px] text-txts mt-0.5">进行中任务</span>
        </div>
      </div>
      <div class="bg-card border border-borderc rounded-card p-5 flex items-center gap-4">
        <div class="w-12 h-12 rounded-card flex items-center justify-center bg-warning/15 text-warning">
          <ClockIcon :size="24" />
        </div>
        <div class="flex flex-col">
          <span class="text-2xl font-semibold">{{ stats.queued_tasks }}</span>
          <span class="text-[13px] text-txts mt-0.5">排队中任务</span>
        </div>
      </div>
      <div class="bg-card border border-borderc rounded-card p-5 flex items-center gap-4">
        <div class="w-12 h-12 rounded-card flex items-center justify-center bg-success/15 text-success">
          <UsersIcon :size="24" />
        </div>
        <div class="flex flex-col">
          <span class="text-2xl font-semibold">{{ stats.total_users }}</span>
          <span class="text-[13px] text-txts mt-0.5">总用户数</span>
        </div>
      </div>
      <div class="bg-card border border-borderc rounded-card p-5 flex items-center gap-4">
        <div class="w-12 h-12 rounded-card flex items-center justify-center bg-danger/15 text-danger">
          <FileTextIcon :size="24" />
        </div>
        <div class="flex flex-col">
          <span class="text-2xl font-semibold">{{ stats.total_tasks }}</span>
          <span class="text-[13px] text-txts mt-0.5">总任务数</span>
        </div>
      </div>
    </div>

    <div class="bg-card border border-borderc rounded-card p-5">
      <h2 class="text-base font-semibold mb-4">服务状态</h2>
      <div class="flex flex-col gap-3">
        <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
          <span class="text-sm text-txts">Redis 连接</span>
          <span class="px-2.5 py-1 rounded text-xs font-medium" :class="stats.redis_connected ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'">
            {{ stats.redis_connected ? '正常' : '异常' }}
          </span>
        </div>
        <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
          <span class="text-sm text-txts">TOS 连接</span>
          <span class="px-2.5 py-1 rounded text-xs font-medium" :class="stats.tos_connected ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'">
            {{ stats.tos_connected ? '正常' : '异常' }}
          </span>
        </div>
        <div class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
          <span class="text-sm text-txts">磁盘使用</span>
          <span class="text-sm font-medium">{{ stats.disk_usage }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Activity, Clock, Users, FileText } from 'lucide-vue-next'
import api from '@/api'
import type { SystemStatus } from '@/types'

const ActivityIcon = Activity
const ClockIcon = Clock
const UsersIcon = Users
const FileTextIcon = FileText

const stats = ref<SystemStatus>({
  active_tasks: 0,
  queued_tasks: 0,
  total_users: 0,
  total_tasks: 0,
  disk_usage: 0,
  redis_connected: false,
  tos_connected: false,
})

async function fetchStatus() {
  try {
    const res = await api.get('/admin/status')
    stats.value = res.data
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取系统状态失败')
  }
}

onMounted(fetchStatus)
</script>


