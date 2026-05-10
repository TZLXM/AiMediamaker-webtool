<template>
  <div class="dashboard-page">
    <h1 class="page-title">系统状态</h1>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(99, 102, 241, 0.15); color: var(--accent);">
          <ActivityIcon :size="24" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.active_tasks }}</span>
          <span class="stat-label">进行中任务</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(245, 158, 11, 0.15); color: var(--accent-warning);">
          <ClockIcon :size="24" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.queued_tasks }}</span>
          <span class="stat-label">排队中任务</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(34, 197, 94, 0.15); color: var(--accent-success);">
          <UsersIcon :size="24" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_users }}</span>
          <span class="stat-label">总用户数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(239, 68, 68, 0.15); color: var(--accent-danger);">
          <FileTextIcon :size="24" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_tasks }}</span>
          <span class="stat-label">总任务数</span>
        </div>
      </div>
    </div>

    <div class="status-section">
      <h2>服务状态</h2>
      <div class="status-list">
        <div class="status-item">
          <span class="status-label">Redis 连接</span>
          <span class="status-badge" :class="stats.redis_connected ? 'success' : 'error'">
            {{ stats.redis_connected ? '正常' : '异常' }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">TOS 连接</span>
          <span class="status-badge" :class="stats.tos_connected ? 'success' : 'error'">
            {{ stats.tos_connected ? '正常' : '异常' }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">磁盘使用</span>
          <span class="status-value">{{ stats.disk_usage }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Activity, Clock, Users, FileText } from 'lucide-vue-next'
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

onMounted(async () => {
  // TODO: 接入实际API
})
</script>

<style scoped>
.page-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.status-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}

.status-section h2 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.status-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.status-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.success {
  background: rgba(34, 197, 94, 0.15);
  color: var(--accent-success);
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.15);
  color: var(--accent-danger);
}

.status-value {
  font-size: 14px;
  font-weight: 500;
}
</style>
