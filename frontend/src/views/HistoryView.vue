<template>
  <div class="history-page">
    <div class="filter-bar">
      <div class="search-box">
        <input v-model="search" placeholder="搜索提示词..." @input="handleSearch" />
      </div>
      <select v-model="modeFilter" @change="handleSearch">
        <option value="all">全部</option>
        <option value="image">图片</option>
        <option value="video">视频</option>
      </select>
    </div>

    <div class="content">
      <div v-if="tasks.length === 0" class="empty">暂无历史任务</div>
      <div v-for="group in groupedTasks" :key="group.date" class="task-group">
        <div class="group-date">{{ group.date }}</div>
        <div class="group-tasks">
          <TaskBlock
            v-for="task in group.tasks"
            :key="task.platform_task_id"
            :task="task"
            show-reuse
            @reuse="goToGenerate(task)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { useTaskStore } from '@/stores'
import type { TaskItem } from '@/types'
import TaskBlock from '@/components/TaskBlock.vue'

const router = useRouter()
const taskStore = useTaskStore()

const tasks = ref<TaskItem[]>([])
const search = ref('')
const modeFilter = ref('all')

const groupedTasks = computed(() => {
  const groups: Record<string, TaskItem[]> = {}
  tasks.value.forEach((task) => {
    const date = dayjs(task.created_at).format('YYYY年MM月DD日')
    if (!groups[date]) groups[date] = []
    groups[date].push(task)
  })
  return Object.entries(groups).map(([date, tasks]) => ({ date, tasks }))
})

async function handleSearch() {
  tasks.value = await taskStore.fetchHistory({
    mode: modeFilter.value === 'all' ? undefined : modeFilter.value,
    search: search.value || undefined,
  })
}

function goToGenerate(task: TaskItem) {
  router.push('/generate')
  // TODO: emit event or store to fill input bar
}

onMounted(handleSearch)
</script>

<style scoped>
.history-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  justify-content: flex-end;
}

.search-box input,
.filter-bar select {
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}

.search-box input {
  width: 240px;
}

.search-box input:focus {
  border-color: var(--accent);
}

.content {
  flex: 1;
  overflow-y: auto;
}

.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 60px 0;
}

.task-group {
  margin-bottom: 24px;
}

.group-date {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
  padding-left: 4px;
}

.group-tasks {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
