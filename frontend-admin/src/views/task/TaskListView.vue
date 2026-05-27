<template>
  <div class="max-w-[1400px]">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-xl font-semibold">任务管理</h1>
      <div class="flex items-center gap-3">
        <input
          v-model="searchKeyword"
          placeholder="搜索提示词/ID..."
          class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-[13px] outline-none focus:border-accent w-56"
          @keyup.enter="fetchTasks"
        />
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
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">远端任务ID</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">用户</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">模式</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">模型</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">状态</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">进度</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">创建时间</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="task in tasks"
            :key="task.id"
            class="cursor-pointer hover:bg-hover"
            @click="openDetail(task)"
          >
            <td class="px-4 py-3 border-t border-borderc font-mono text-xs text-txts">{{ task.platform_task_id }}</td>
            <td class="px-4 py-3 border-t border-borderc font-mono text-xs text-txts">{{ task.remote_task_id || '-' }}</td>
            <td class="px-4 py-3 border-t border-borderc">{{ task.username }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <span class="px-2 py-0.5 rounded text-xs font-medium" :class="task.mode === 'image' ? 'bg-accent/15 text-accent' : 'bg-warning/15 text-warning'">{{ task.mode === 'image' ? '图片' : '视频' }}</span>
            </td>
            <td class="px-4 py-3 border-t border-borderc font-mono text-xs text-txts">{{ task.model_id }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <span class="px-2 py-0.5 rounded text-xs" :class="statusClass(task.status)">{{ statusLabel(task.status) }}</span>
            </td>
            <td class="px-4 py-3 border-t border-borderc">
              <div v-if="task.status === 'running'" class="w-24 h-1.5 bg-active rounded-full overflow-hidden">
                <div class="h-full bg-accent rounded-full animate-progress-indeterminate"></div>
              </div>
              <span v-else class="text-xs text-txtm">-</span>
            </td>
            <td class="px-4 py-3 border-t border-borderc">{{ formatDate(task.created_at) }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <button
                v-if="['pending','queued','running'].includes(task.status)"
                class="px-2 py-1 bg-transparent border-none text-danger text-[13px] cursor-pointer"
                @click.stop="cancelTask(task)"
              >
                取消
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="tasks.length === 0" class="text-center py-10 text-txtm text-sm">暂无任务</div>

      <!-- 分页 -->
      <div class="flex items-center justify-between px-4 py-3 border-t border-borderc">
        <span class="text-xs text-txts">第 {{ page }} 页</span>
        <div class="flex gap-2">
          <button
            class="px-3 h-8 bg-active border border-borderc rounded-btn text-txts text-[13px] cursor-pointer hover:bg-hover disabled:opacity-40 disabled:cursor-not-allowed"
            :disabled="page <= 1"
            @click="prevPage"
          >
            上一页
          </button>
          <button
            class="px-3 h-8 bg-active border border-borderc rounded-btn text-txts text-[13px] cursor-pointer hover:bg-hover disabled:opacity-40 disabled:cursor-not-allowed"
            :disabled="tasks.length < pageSize"
            @click="nextPage"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 任务详情弹窗 -->
    <div
      v-if="detailTask"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-[1000]"
      @click.self="detailTask = null"
    >
      <div class="bg-card border border-borderc rounded-card p-6 w-[480px]">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-base font-semibold">任务详情</h3>
          <button class="text-txts hover:text-txtp cursor-pointer" @click="detailTask = null">
            <XIcon :size="18" />
          </button>
        </div>
        <div class="flex flex-col gap-4">
          <div class="flex justify-between items-center">
            <span class="text-[13px] text-txts">平台任务ID</span>
            <span class="font-mono text-xs text-txtp">{{ detailTask.platform_task_id }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-[13px] text-txts">远端任务ID</span>
            <span class="font-mono text-xs text-txtp">{{ detailTask.remote_task_id || '-' }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-[13px] text-txts">用户</span>
            <span class="text-sm text-txtp">{{ detailTask.username }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-[13px] text-txts">状态</span>
            <span class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full" :class="statusDotClass(detailTask.status)"></span>
              <span class="text-sm" :class="statusClass(detailTask.status)">{{ statusLabel(detailTask.status) }}</span>
            </span>
          </div>
          <div class="flex flex-col gap-1.5">
            <span class="text-[13px] text-txts">提示词</span>
            <p class="text-sm text-txtp bg-active rounded-btn p-3">{{ detailTask.prompt || '-' }}</p>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-[13px] text-txts">创建时间</span>
            <span class="text-sm text-txtp">{{ formatDateTime(detailTask.created_at) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-[13px] text-txts">完成时间</span>
            <span class="text-sm text-txtp">{{ detailTask.completed_at ? formatDateTime(detailTask.completed_at) : '-' }}</span>
          </div>
        </div>
        <div class="flex justify-end mt-6">
          <button class="px-4 h-9 bg-active border border-borderc rounded-btn text-txts text-[13px] cursor-pointer hover:bg-hover" @click="detailTask = null">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RefreshCw, X } from 'lucide-vue-next'
import dayjs from 'dayjs'
import api from '@/api'
import type { AdminTask } from '@/types'

const RefreshIcon = RefreshCw
const XIcon = X

const tasks = ref<AdminTask[]>([])
const filterMode = ref('')
const filterStatus = ref('')
const searchKeyword = ref('')
const page = ref(1)
const pageSize = 20
const detailTask = ref<AdminTask | null>(null)

async function fetchTasks() {
  try {
    const params: Record<string, any> = {
      page: page.value,
      page_size: pageSize,
    }
    if (filterMode.value) params.mode = filterMode.value
    if (filterStatus.value) params.status = filterStatus.value
    if (searchKeyword.value.trim()) params.search = searchKeyword.value.trim()
    const res = await api.get('/admin/tasks', { params })
    tasks.value = res.data
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取任务列表失败')
  }
}

function prevPage() {
  if (page.value <= 1) return
  page.value--
  fetchTasks()
}

function nextPage() {
  page.value++
  fetchTasks()
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

function statusDotClass(status: string) {
  const map: Record<string, string> = {
    pending: 'bg-txtm',
    queued: 'bg-warning',
    running: 'bg-accent',
    succeeded: 'bg-success',
    failed: 'bg-danger',
    cancelled: 'bg-txtm',
  }
  return map[status] || 'bg-txtm'
}

function formatDate(d: string) {
  return dayjs(d).format('MM-DD HH:mm')
}

function formatDateTime(d: string) {
  return dayjs(d).format('YYYY-MM-DD HH:mm:ss')
}

function openDetail(task: AdminTask) {
  detailTask.value = task
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

<style scoped>
@keyframes progress-indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(300%); }
}
.animate-progress-indeterminate {
  animation: progress-indeterminate 1.5s ease-in-out infinite;
  width: 40%;
}
</style>
