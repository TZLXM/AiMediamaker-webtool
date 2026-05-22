<template>
  <div class="assets-page">
    <div class="filter-bar">
      <div class="search-box">
        <input v-model="search" placeholder="搜索文件名..." @input="handleSearch" />
      </div>
      <select v-model="typeFilter" @change="handleSearch">
        <option value="all">全部</option>
        <option value="image">图片</option>
        <option value="video">视频</option>
      </select>
    </div>

    <div class="content">
      <div v-if="assets.length === 0" class="empty">暂无生成资产</div>
      <div v-for="group in groupedAssets" :key="group.date" class="asset-group">
        <div class="group-date">{{ group.date }}</div>
        <div class="group-grid">
          <div
            v-for="asset in group.assets"
            :key="asset.file_id"
            class="asset-item"
            @click="openPreview(asset)"
          >
            <div class="asset-thumb-wrap">
              <img v-if="asset.file_type === 'image'" :src="getFileUrl(asset)" :alt="asset.original_name" />
              <video v-else-if="asset.file_type === 'video'" :src="getFileUrl(asset)" />
              <div v-else class="audio-icon">Audio</div>
              <div v-if="asset.file_type === 'video'" class="video-badge">视频</div>
            </div>
            <div class="asset-overlay">
              <span class="asset-name">{{ asset.original_name }}</span>
              <button class="asset-download" @click.stop="downloadAsset(asset)">
                <DownloadIcon :size="14" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { Download as DownloadIcon } from 'lucide-vue-next'
import api from '@/api'
import { usePreviewStore } from '@/stores'
import { getFileUrl } from '@/utils/fileUrl'
import type { FileItem } from '@/types'

const previewStore = usePreviewStore()

const assets = ref<FileItem[]>([])
const search = ref('')
const typeFilter = ref('all')

const groupedAssets = computed(() => {
  const groups: Record<string, FileItem[]> = {}
  assets.value.forEach((a) => {
    const date = dayjs(a.created_at).format('YYYY年MM月DD日')
    if (!groups[date]) groups[date] = []
    groups[date].push(a)
  })
  return Object.entries(groups).map(([date, assets]) => ({ date, assets }))
})

async function handleSearch() {
  const res = await api.get('/files/assets/list', {
    params: {
      file_type: typeFilter.value === 'all' ? undefined : typeFilter.value,
      search: search.value || undefined,
    },
  })
  assets.value = res.data
}

function openPreview(asset: FileItem) {
  previewStore.openPreview(asset)
}

function downloadAsset(asset: FileItem) {
  const a = document.createElement('a')
  a.href = getFileUrl(asset)
  a.download = asset.original_name
  a.click()
}

onMounted(handleSearch)
</script>

<style scoped>
.assets-page {
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
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-primary);
  font-size: 13px;
  outline: none;
}

.search-box input {
  width: 240px;
}

.search-box input:focus {
  border-color: var(--color-accent);
}

.content {
  flex: 1;
  overflow-y: auto;
}

.empty {
  text-align: center;
  color: var(--color-text-muted);
  padding: 60px 0;
}

.asset-group {
  margin-bottom: 24px;
}

.group-date {
  font-size: 12px;
  color: var(--color-text-muted);
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
  transition: transform 0.2s;
}

.asset-item:hover {
  transform: scale(1.02);
}

.asset-thumb-wrap {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.asset-thumb-wrap img,
.asset-thumb-wrap video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: var(--color-bg-tertiary);
  transition: transform 0.3s ease;
}

.asset-item:hover .asset-thumb-wrap img,
.asset-item:hover .asset-thumb-wrap video {
  transform: scale(1.05);
}

.audio-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--color-text-muted);
}

.video-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.asset-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  display: flex;
  align-items: center;
  justify-content: space-between;
  opacity: 0;
  transition: opacity 0.2s;
}

.asset-item:hover .asset-overlay {
  opacity: 1;
}

.asset-name {
  font-size: 12px;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70%;
}

.asset-download {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
</style>
