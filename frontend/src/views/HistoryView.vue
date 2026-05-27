<template>
  <div class="history-page">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <!-- 时间筛选 -->
        <div class="filter-wrap" ref="timeWrapRef">
          <button
            class="filter-pill"
            :class="{ active: hasTimeFilter }"
            @click="toggleTimeDropdown"
          >
            <span>{{ timeLabel }}</span>
            <ChevronDownIcon :size="14" class="chevron" :class="{ open: showTimeDropdown }" />
          </button>
          <div v-if="showTimeDropdown" class="dropdown-menu">
            <div class="preset-options">
              <button
                v-for="opt in timePresets"
                :key="opt.value"
                class="preset-btn"
                :class="{ active: timePreset === opt.value }"
                @click="selectTimePreset(opt.value)"
              >
                {{ opt.label }}
              </button>
            </div>
            <div class="divider" />
            <div class="date-range">
              <div class="date-cell">
                <span class="date-label">开始日期</span>
                <div class="date-input">
                  <CalendarIcon :size="14" />
                  <input
                    v-model="startDate"
                    type="date"
                    placeholder="YYYY/MM/DD"
                    @change="onCustomDateChange"
                  />
                </div>
              </div>
              <span class="date-sep">-</span>
              <div class="date-cell">
                <span class="date-label">结束日期</span>
                <div class="date-input">
                  <CalendarIcon :size="14" />
                  <input
                    v-model="endDate"
                    type="date"
                    placeholder="YYYY/MM/DD"
                    @change="onCustomDateChange"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 类型筛选 -->
        <div class="filter-wrap" ref="modeWrapRef">
          <button
            class="filter-pill"
            :class="{ active: modeFilter !== 'all' }"
            @click="toggleModeDropdown"
          >
            <span>{{ modeLabel }}</span>
            <ChevronDownIcon :size="14" class="chevron" :class="{ open: showModeDropdown }" />
          </button>
          <div v-if="showModeDropdown" class="dropdown-menu simple">
            <button
              v-for="opt in modeOptions"
              :key="opt.value"
              class="list-option"
              :class="{ active: modeFilter === opt.value }"
              @click="selectMode(opt.value)"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- 搜索框 -->
      <div class="search-box">
        <SearchIcon :size="14" class="search-icon" />
        <input
          v-model="search"
          placeholder="搜索提示词..."
          @input="handleSearchInput"
        />
        <button v-if="search" class="clear-btn" @click="clearSearch">
          <XIcon :size="12" />
        </button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="content">
      <div v-if="loading" class="loading-state">
        <div class="spinner" />
        <span>加载中...</span>
      </div>
      <div v-else-if="tasks.length === 0" class="empty">
        <ClockIcon :size="40" class="empty-icon" />
        <p>暂无历史任务</p>
      </div>
      <div v-else>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import {
  ChevronDown as ChevronDownIcon,
  Search as SearchIcon,
  X as XIcon,
  Calendar as CalendarIcon,
  Clock as ClockIcon,
} from 'lucide-vue-next'
import { useTaskStore } from '@/stores'
import type { TaskItem } from '@/types'
import TaskBlock from '@/components/TaskBlock.vue'

const router = useRouter()
const taskStore = useTaskStore()

const tasks = ref<TaskItem[]>([])
const loading = ref(false)
const search = ref('')
const modeFilter = ref('all')
const timePreset = ref('all')
const startDate = ref('')
const endDate = ref('')

const showTimeDropdown = ref(false)
const showModeDropdown = ref(false)
const timeWrapRef = ref<HTMLElement | null>(null)
const modeWrapRef = ref<HTMLElement | null>(null)

const timePresets = [
  { value: 'all', label: '全部时间' },
  { value: 'week', label: '最近一周' },
  { value: 'month', label: '最近一个月' },
  { value: 'quarter', label: '最近三个月' },
]

const modeOptions = [
  { value: 'all', label: '全部' },
  { value: 'image', label: '图片' },
  { value: 'video', label: '视频' },
]

const timeLabel = computed(() => {
  if (timePreset.value !== 'all') {
    return timePresets.find((p) => p.value === timePreset.value)?.label || '全部时间'
  }
  if (startDate.value || endDate.value) {
    const s = startDate.value ? dayjs(startDate.value).format('MM/DD') : ''
    const e = endDate.value ? dayjs(endDate.value).format('MM/DD') : ''
    return s && e ? `${s} - ${e}` : s || e || '自定义'
  }
  return '全部时间'
})

const modeLabel = computed(() => {
  return modeOptions.find((m) => m.value === modeFilter.value)?.label || '全部'
})

const hasTimeFilter = computed(() => {
  return timePreset.value !== 'all' || startDate.value !== '' || endDate.value !== ''
})

function toggleTimeDropdown() {
  showTimeDropdown.value = !showTimeDropdown.value
  showModeDropdown.value = false
}

function toggleModeDropdown() {
  showModeDropdown.value = !showModeDropdown.value
  showTimeDropdown.value = false
}

function selectTimePreset(value: string) {
  timePreset.value = value
  startDate.value = ''
  endDate.value = ''
  showTimeDropdown.value = false
  loadTasks()
}

function onCustomDateChange() {
  timePreset.value = 'all'
  loadTasks()
}

function selectMode(value: string) {
  modeFilter.value = value
  showModeDropdown.value = false
  loadTasks()
}

function clearSearch() {
  search.value = ''
  loadTasks()
}

let searchDebounce: ReturnType<typeof setTimeout>
function handleSearchInput() {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    loadTasks()
  }, 300)
}

function getDateRange() {
  let s: string | undefined
  let e: string | undefined

  if (timePreset.value === 'week') {
    s = dayjs().subtract(7, 'day').startOf('day').toISOString()
  } else if (timePreset.value === 'month') {
    s = dayjs().subtract(1, 'month').startOf('day').toISOString()
  } else if (timePreset.value === 'quarter') {
    s = dayjs().subtract(3, 'month').startOf('day').toISOString()
  } else {
    if (startDate.value) {
      s = dayjs(startDate.value).startOf('day').toISOString()
    }
    if (endDate.value) {
      e = dayjs(endDate.value).startOf('day').toISOString()
    }
  }

  return { start_date: s, end_date: e }
}

async function loadTasks() {
  loading.value = true
  const { start_date, end_date } = getDateRange()
  try {
    tasks.value = await taskStore.fetchHistory({
      mode: modeFilter.value === 'all' ? undefined : modeFilter.value,
      search: search.value || undefined,
      start_date,
      end_date,
    })
  } finally {
    loading.value = false
  }
}

const groupedTasks = computed(() => {
  const groups: Record<string, TaskItem[]> = {}
  tasks.value.forEach((task) => {
    const date = dayjs(task.created_at).format('YYYY年MM月DD日')
    if (!groups[date]) groups[date] = []
    groups[date].push(task)
  })
  return Object.entries(groups).map(([date, tasks]) => ({ date, tasks }))
})

function goToGenerate(task: TaskItem) {
  router.push({
    path: '/generate',
    query: { reuse_task_id: task.platform_task_id },
  })
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (timeWrapRef.value && !timeWrapRef.value.contains(target)) {
    showTimeDropdown.value = false
  }
  if (modeWrapRef.value && !modeWrapRef.value.contains(target)) {
    showModeDropdown.value = false
  }
}

onMounted(() => {
  loadTasks()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.history-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 16px 24px 60px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-default);
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-wrap {
  position: relative;
}

.filter-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  background: var(--input-bg);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  color: var(--text-secondary);
  font-family: inherit;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-pill:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.filter-pill.active {
  color: var(--accent-hover);
  background: #6366f11a;
  border-color: #6366f140;
}

.chevron {
  transition: transform 0.2s;
}

.chevron.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 100;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-hover);
  border-radius: 12px;
  min-width: 260px;
  padding: 12px;
  box-shadow: var(--shadow-modal);
}

.dropdown-menu.simple {
  min-width: 140px;
}

.preset-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.preset-btn {
  padding: 4px 10px;
  background: var(--input-bg);
  border: 1px solid var(--border-default);
  border-radius: 6px;
  color: var(--text-secondary);
  font-family: inherit;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.preset-btn.active {
  color: var(--accent-hover);
  background: #6366f11a;
  border-color: #6366f140;
}

.divider {
  height: 1px;
  background: var(--border-default);
  margin: 10px 0;
}

.date-range {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.date-cell {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date-label {
  font-size: 11px;
  color: var(--text-tertiary);
  padding-left: 2px;
}

.date-input {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 8px;
  background: var(--input-bg);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  transition: border-color 0.2s;
}

.date-input:focus-within {
  border-color: var(--accent);
}

.date-input input {
  flex: 1;
  width: 0;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 12px;
}

.date-input input::placeholder {
  color: var(--text-tertiary);
}

.date-input svg {
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.date-sep {
  color: var(--text-tertiary);
  font-size: 12px;
  padding-bottom: 6px;
}

.list-option {
  display: block;
  width: 100%;
  text-align: left;
  padding: 8px 10px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-secondary);
  font-family: inherit;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.list-option:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.list-option.active {
  color: var(--accent-hover);
  background: #6366f11a;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box input {
  width: 220px;
  height: 34px;
  padding: 0 32px;
  background: var(--input-bg);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: var(--accent);
}

.search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-tertiary);
  pointer-events: none;
}

.clear-btn {
  position: absolute;
  right: 8px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--bg-hover);
  border: none;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.clear-btn:hover {
  color: var(--text-primary);
}

.content {
  flex: 1;
  overflow-y: auto;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #ffffff14;
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 0;
  color: var(--text-muted);
  font-size: 14px;
}

.empty-icon {
  color: var(--text-muted);
  opacity: 0.5;
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
