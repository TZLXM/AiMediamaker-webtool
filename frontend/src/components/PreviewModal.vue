<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="previewStore.preview.visible"
        class="preview-overlay"
        @click.self="previewStore.closePreview"
      >
        <button class="preview-close" @click="previewStore.closePreview">
          <XIcon :size="18" />
        </button>
        <button class="preview-download" @click="downloadFile">
          <DownloadIcon :size="18" />
        </button>

        <!-- 图片预览 -->
        <div
          v-if="!previewStore.preview.isVideo && file"
          class="image-preview-container"
          @wheel.prevent="handleZoom"
          @mousedown.prevent="startDrag"
          @mousemove="onDrag"
          @mouseup="endDrag"
          @mouseleave="endDrag"
        >
          <img
            :src="fileUrl"
            class="preview-image"
            :style="imageStyle"
            alt="Preview"
            draggable="false"
          />
          <div v-if="scale > 1" class="zoom-hint">{{ Math.round(scale * 100) }}%</div>
        </div>

        <!-- 视频预览 -->
        <div v-if="previewStore.preview.isVideo && file" class="video-preview-container">
          <video
            ref="videoRef"
            :src="fileUrl"
            class="preview-video"
            @click="togglePlay"
            @timeupdate="onTimeUpdate"
            @loadedmetadata="onLoadedMeta"
            autoplay
          />
          <div class="video-controls">
            <button class="control-btn" @click="togglePlay">
              <PauseIcon v-if="isPlaying" :size="18" />
              <PlayIcon v-else :size="18" />
            </button>
            <div class="progress-bar" @click="seek">
              <div class="progress-track">
                <div class="progress-fill" :style="{ width: progress + '%' }" />
              </div>
            </div>
            <span class="time-display">{{ currentTime }} / {{ duration }}</span>
            <div class="volume-control">
              <VolumeIcon :size="14" />
              <input
                v-model="volume"
                type="range"
                min="0"
                max="100"
                class="volume-slider"
                @input="onVolumeChange"
              />
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { X as XIcon, Download as DownloadIcon, Play as PlayIcon, Pause as PauseIcon, Volume2 as VolumeIcon } from 'lucide-vue-next'
import { usePreviewStore } from '@/stores'
import { getFileUrl } from '@/utils/fileUrl'

const previewStore = usePreviewStore()
const file = computed(() => previewStore.preview.file)
const fileUrl = computed(() => file.value ? getFileUrl(file.value) : '')

// Image zoom & pan
const scale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

const imageStyle = computed(() => ({
  transform: `translate(${offsetX.value}px, ${offsetY.value}px) scale(${scale.value})`,
  cursor: isDragging.value ? 'grabbing' : scale.value > 1 ? 'grab' : 'default',
}))

function handleZoom(e: WheelEvent) {
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  scale.value = Math.max(0.1, Math.min(5, scale.value + delta))
}

function startDrag(e: MouseEvent) {
  if (scale.value <= 1) return
  isDragging.value = true
  dragStart.value = { x: e.clientX - offsetX.value, y: e.clientY - offsetY.value }
}

function onDrag(e: MouseEvent) {
  if (!isDragging.value) return
  offsetX.value = e.clientX - dragStart.value.x
  offsetY.value = e.clientY - dragStart.value.y
}

function endDrag() {
  isDragging.value = false
}

// Video controls
const videoRef = ref<HTMLVideoElement | null>(null)
const isPlaying = ref(true)
const progress = ref(0)
const currentTime = ref('0:00')
const duration = ref('0:00')
const volume = ref(80)

watch(
  () => previewStore.preview.visible,
  (visible) => {
    if (visible) {
      scale.value = 1
      offsetX.value = 0
      offsetY.value = 0
      isPlaying.value = true
      progress.value = 0
    }
  }
)

function togglePlay() {
  if (!videoRef.value) return
  if (videoRef.value.paused) {
    videoRef.value.play()
    isPlaying.value = true
  } else {
    videoRef.value.pause()
    isPlaying.value = false
  }
}

function onTimeUpdate() {
  if (!videoRef.value) return
  const pct = (videoRef.value.currentTime / videoRef.value.duration) * 100
  progress.value = pct || 0
  currentTime.value = formatTime(videoRef.value.currentTime)
}

function onLoadedMeta() {
  if (!videoRef.value) return
  duration.value = formatTime(videoRef.value.duration)
}

function seek(e: MouseEvent) {
  if (!videoRef.value) return
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  const pct = (e.clientX - rect.left) / rect.width
  videoRef.value.currentTime = pct * videoRef.value.duration
}

function onVolumeChange() {
  if (!videoRef.value) return
  videoRef.value.volume = volume.value / 100
}

function formatTime(t: number) {
  if (!isFinite(t)) return '0:00'
  const m = Math.floor(t / 60)
  const s = Math.floor(t % 60)
    .toString()
    .padStart(2, '0')
  return `${m}:${s}`
}

function downloadFile() {
  if (!file.value) return
  const a = document.createElement('a')
  a.href = fileUrl.value
  a.download = file.value.original_name
  a.target = '_blank'
  a.click()
}
</script>

<style scoped>
.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.preview-close,
.preview-download {
  position: absolute;
  top: 16px;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.preview-close {
  right: 16px;
}

.preview-download {
  right: 60px;
}

.preview-close:hover,
.preview-download:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.image-preview-container {
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  user-select: none;
}

.zoom-hint {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.video-preview-container {
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.preview-video {
  max-width: 100%;
  max-height: 80vh;
  cursor: pointer;
}

.video-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--color-bg-secondary);
  border-radius: 0 0 8px 8px;
}

.control-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-bg-tertiary);
  border: none;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--color-bg-tertiary);
  border-radius: 2px;
  cursor: pointer;
  position: relative;
}

.progress-track {
  height: 100%;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-accent);
  border-radius: 2px;
}

.time-display {
  font-size: 12px;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-secondary);
}

.volume-slider {
  width: 80px;
  accent-color: var(--color-accent);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
