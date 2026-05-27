<template>
  <div class="assets-page">
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
        <div class="filter-wrap" ref="typeWrapRef">
          <button
            class="filter-pill"
            :class="{ active: typeFilter !== 'all' }"
            @click="toggleTypeDropdown"
          >
            <span>{{ typeLabel }}</span>
            <ChevronDownIcon :size="14" class="chevron" :class="{ open: showTypeDropdown }" />
          </button>
          <div v-if="showTypeDropdown" class="dropdown-menu simple">
            <button
              v-for="opt in typeOptions"
              :key="opt.value"
              class="list-option"
              :class="{ active: typeFilter === opt.value }"
              @click="selectType(opt.value)"
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
          placeholder="搜索文件名..."
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
      <div v-else-if="assets.length === 0" class="empty">
        <ImageIcon :size="40" class="empty-icon" />
        <p>暂无生成资产</p>
      </div>
      <div v-else>
        <div v-for="group in groupedAssets" :key="group.date" class="asset-group">
          <div class="group-date">{{ group.date }}</div>
          <div class="group-grid">
            <div
              v-for="asset in group.assets"
              :key="asset.file_id"
              class="asset-item"
              @click="openPreview(asset)"
            >
              <Thumbnail
                :file="asset"
                show-download
                show-delete
                @click="openPreview(asset)"
                @delete="handleDelete(asset)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import {
  ChevronDown as ChevronDownIcon,
  Search as SearchIcon,
  X as XIcon,
  Calendar as CalendarIcon,
  Image as ImageIcon,
} from 'lucide-vue-next'
import { useTaskStore, usePreviewStore } from '@/stores'
import Thumbnail from '@/components/Thumbnail.vue'
import type { FileItem } from '@/types'

const taskStore = useTaskStore()
const previewStore = usePreviewStore()

const assets = ref<FileItem[]>([])
const loading = ref(false)
const search = ref('')
const typeFilter = ref('all')
const timePreset = ref('all')
const startDate = ref('')
const endDate = ref('')

const showTimeDropdown = ref(false)
const showTypeDropdown = ref(false)
const timeWrapRef = ref<HTMLElement | null>(null)
const typeWrapRef = ref<HTMLElement | null>(null)

const timePresets = [
  { value: 'all', label: '全部时间' },
  { value: 'week', label: '最近一周' },
  { value: 'month', label: '最近一个月' },
  { value: 'quarter', label: '最近三个月' },
]

const typeOptions = [
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

const typeLabel = computed(() => {
  return typeOptions.find((t) => t.value === typeFilter.value)?.label || '全部'
})

const hasTimeFilter = computed(() => {
  return timePreset.value !== 'all' || startDate.value !== '' || endDate.value !== ''
})

function toggleTimeDropdown() {
  showTimeDropdown.value = !showTimeDropdown.value
  showTypeDropdown.value = false
}

function toggleTypeDropdown() {
  showTypeDropdown.value = !showTypeDropdown.value
  showTimeDropdown.value = false
}

function selectTimePreset(value: string) {
  timePreset.value = value
  startDate.value = ''
  endDate.value = ''
  showTimeDropdown.value = false
  loadAssets()
}

function onCustomDateChange() {
  timePreset.value = 'all'
  loadAssets()
}

function selectType(value: string) {
  typeFilter.value = value
  showTypeDropdown.value = false
  loadAssets()
}

function clearSearch() {
  search.value = ''
  loadAssets()
}

let searchDebounce: ReturnType<typeof setTimeout>
function handleSearchInput() {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    loadAssets()
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

async function loadAssets() {
  loading.value = true
  const { start_date, end_date } = getDateRange()
  try {
    assets.value = await taskStore.fetchAssets({
      file_type: typeFilter.value === 'all' ? undefined : typeFilter.value,
      search: search.value || undefined,
      start_date,
      end_date,
      page: 1,
      page_size: 999,
    })
  } finally {
    loading.value = false
  }
}

const groupedAssets = computed(() => {
  const groups: Record<string, FileItem[]> = {}
  assets.value.forEach((a) => {
    const date = dayjs(a.created_at).format('YYYY年MM月DD日')
    if (!groups[date]) groups[date] = []
    groups[date].push(a)
  })
  return Object.entries(groups).map(([date, assets]) => ({ date, assets }))
})

function openPreview(asset: FileItem) {
  previewStore.openPreview(asset)
}

async function handleDelete(asset: FileItem) {
  if (!confirm('确定要删除该文件吗？')) return
  try {
    await taskStore.deleteFile(asset.file_id)
    // 从当前列表中移除
    assets.value = assets.value.filter((a) => a.file_id !== asset.file_id)
  } catch {
    alert('删除失败')
  }
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (timeWrapRef.value && !timeWrapRef.value.contains(target)) {
    showTimeDropdown.value = false
  }
  if (typeWrapRef.value && !typeWrapRef.value.contains(target)) {
    showTypeDropdown.value = false
  }
}

onMounted(() => {
  loadAssets()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.assets-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px 40px;
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

.asset-group {
  margin-bottom: 24px;
}

.group-date {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
  padding-left: 4px;
}

.group-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.asset-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 10px;
  overflow: hidden;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.asset-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}
</style>
