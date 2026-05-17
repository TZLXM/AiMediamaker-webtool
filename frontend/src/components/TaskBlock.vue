<template>
  <div class="task-block" :class="`status-${task.status}`">
    <div class="task-prompt">{{ task.prompt }}</div>

    <div v-if="task.input_files?.length" class="task-files">
      <div
        v-for="file in task.input_files"
        :key="file.file_id"
        class="task-file-thumb"
        @click="previewStore.openPreview(file)"
      >
        <img v-if="file.file_type === 'image'" :src="getFileUrl(file)" />
        <video v-else-if="file.file_type === 'video'" :src="getFileUrl(file)" />
        <div v-else class="audio-badge">Audio</div>
      </div>
    </div>

    <div class="task-meta">
      <span class="meta-badge mode">{{ task.mode === 'image' ? '图片' : '视频' }}</span>
      <span class="meta-badge model">{{ modelName }}</span>
      <span v-for="(val, key) in displayParams" :key="key" class="meta-badge param">
        {{ key }}: {{ val }}
      </span>
    </div>

    <div class="task-outputs">
      <template v-if="task.output_files?.length">
        <div class="output-grid">
          <div
            v-for="file in task.output_files"
            :key="file.file_id"
            class="output-thumb"
            @click="previewStore.openPreview(file)"
          >
            <img v-if="file.file_type === 'image'" :src="getFileUrl(file)" />
            <video v-else-if="file.file_type === 'video'" :src="getFileUrl(file)" />
          </div>
        </div>
      </template>
      <template v-else>
        <div class="status-display">
          <span v-if="task.status === 'pending'">等待中...</span>
          <span v-else-if="task.status === 'queued'">排队中...</span>
          <span v-else-if="task.status === 'running'">生成中...</span>
          <span v-else-if="task.status === 'downloading'">下载结果中...</span>
          <span v-else-if="task.status === 'cancelled'">已取消</span>
          <span v-else-if="task.status === 'failed'" class="error">
            失败 {{ task.error_code ? `(${task.error_code})` : '' }}
          </span>
        </div>
      </template>
    </div>

    <div class="task-footer">
      <button v-if="showReuse" class="reuse-btn" @click="$emit('reuse')">
        <RefreshIcon :size="12" />
        <span>复用</span>
      </button>
      <span v-if="task.completed_at" class="task-time">
        {{ formatTime(task.completed_at) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RefreshCw as RefreshIcon } from 'lucide-vue-next'
import dayjs from 'dayjs'
import { usePreviewStore } from '@/stores'
import { getFileUrl } from '@/utils/fileUrl'
import type { TaskItem } from '@/types'

const props = defineProps<{
  task: TaskItem
  showReuse?: boolean
}>()

defineEmits<{
  (e: 'reuse'): void
}>()

const previewStore = usePreviewStore()

const modelName = computed(() => {
  // 简化显示，实际应从模型列表匹配
  return props.task.model_id
})

const displayParams = computed(() => {
  const p = props.task.parameters || {}
  const result: Record<string, string> = {}
  if (p.ratio) result['比例'] = p.ratio
  if (p.duration) result['时长'] = `${p.duration}s`
  if (p.size) result['尺寸'] = p.size
  if (p.output_format) result['格式'] = p.output_format
  return result
})

function formatTime(t: string) {
  return dayjs(t).format('MM-DD HH:mm')
}
</script>

<style scoped>
.task-block {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.task-prompt {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 10px;
  white-space: pre-wrap;
  word-break: break-word;
}

.task-files {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.task-file-thumb {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-bg-tertiary);
  cursor: pointer;
}

.task-file-thumb img,
.task-file-thumb video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: var(--color-bg-tertiary);
}

.audio-badge {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--color-text-muted);
}

.task-meta {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.meta-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}

.meta-badge.mode {
  background: var(--color-accent);
  color: white;
}

.task-outputs {
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.output-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  width: 100%;
}

.output-thumb {
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-bg-tertiary);
  cursor: pointer;
}

.output-thumb img,
.output-thumb video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: var(--color-bg-tertiary);
}

.status-display {
  font-size: 13px;
  color: var(--color-text-muted);
}

.status-display .error {
  color: var(--error);
}

.task-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--color-border);
}

.reuse-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  color: var(--color-text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.reuse-btn:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-secondary);
}

.task-time {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-left: auto;
}
</style>
