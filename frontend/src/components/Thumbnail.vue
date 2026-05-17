<template>
  <div
    class="thumbnail-wrapper"
    :class="{ 'in-input': size === 'small', 'is-audio': file.file_type === 'audio' }"
    @click="handleClick"
  >
    <div class="thumbnail-container">
      <img
        v-if="file.file_type === 'image'"
        :src="getFileUrl(file)"
        class="thumbnail-img"
        :alt="file.original_name"
        draggable="false"
      />
      <template v-else-if="file.file_type === 'video'">
        <img
          v-if="file.thumbnail_url"
          :src="file.thumbnail_url"
          class="thumbnail-img"
          draggable="false"
        />
        <video v-else :src="getFileUrl(file)" class="thumbnail-img" />
        <div class="video-overlay">
          <PlayIcon :size="20" class="play-icon" />
        </div>
      </template>
      <div v-else class="audio-thumbnail">
        <MusicIcon :size="20" />
        <span class="audio-format">{{ audioFormat }}</span>
      </div>
    </div>

    <!-- 删除按钮 -->
    <button
      v-if="showDelete"
      class="delete-btn"
      @click.stop="$emit('delete')"
    >
      <XIcon :size="12" />
    </button>

    <!-- Hover 遮罩（仅非小尺寸） -->
    <div v-if="size !== 'small'" class="hover-overlay">
      <span class="filename">{{ file.original_name }}</span>
      <button
        v-if="showDownload"
        class="download-btn"
        @click.stop="handleDownload"
      >
        <DownloadIcon :size="14" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Play as PlayIcon, Music as MusicIcon, X as XIcon, Download as DownloadIcon } from 'lucide-vue-next'
import { getFileUrl } from '@/utils/fileUrl'
import type { FileItem } from '@/types'

const props = defineProps<{
  file: FileItem
  size?: 'small' | 'normal'
  showDelete?: boolean
  showDownload?: boolean
}>()

const emit = defineEmits<{
  (e: 'delete'): void
  (e: 'click'): void
}>()

const audioFormat = computed(() => {
  const ext = props.file.original_name.split('.').pop()?.toUpperCase()
  return ext || 'AUDIO'
})

function handleClick() {
  emit('click')
}

function handleDownload() {
  const a = document.createElement('a')
  a.href = getFileUrl(props.file)
  a.download = props.file.original_name
  a.click()
}
</script>

<style scoped>
.thumbnail-wrapper {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
}

.thumbnail-wrapper:not(.in-input) {
  aspect-ratio: 1;
  width: 100%;
}

.thumbnail-wrapper.in-input {
  width: 64px;
  height: 64px;
}

.thumbnail-container {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.thumbnail-wrapper:hover .thumbnail-img {
  transform: scale(1.05);
}

.video-overlay {
  position: absolute;
  inset: 0;
  background: #0000004d;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: background 0.2s;
}

.video-overlay .play-icon {
  color: #fff;
  opacity: 0.9;
}

.thumbnail-wrapper:hover .video-overlay {
  background: #00000080;
}

.audio-thumbnail {
  width: 100%;
  height: 100%;
  background: var(--color-bg-tertiary);
  color: var(--color-text-muted);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
}

.audio-format {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.05em;
}

.delete-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #00000099;
  border: none;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: background 0.2s;
  z-index: 2;
}

.delete-btn:hover {
  background: #ef4444cc;
}

.hover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(#00000000 50%, #000000b3 100%);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.thumbnail-wrapper:hover .hover-overlay {
  opacity: 1;
}

.filename {
  color: #fff;
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.download-btn {
  position: absolute;
  bottom: 8px;
  left: 8px;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: #ffffff26;
  border: none;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: background 0.2s;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.download-btn:hover {
  background: #ffffff4d;
}
</style>
