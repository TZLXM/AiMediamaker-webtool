<template>
  <div class="task-block" :class="`status-${task.status}`">
    <!-- 提示词 -->
    <div class="task-prompt">
      <p
        class="prompt-text"
        :class="{ expanded: isPromptExpanded }"
        :title="isPromptExpanded ? '点击收起' : '点击展开'"
        @click="isPromptExpanded = !isPromptExpanded"
      >
        {{ task.prompt }}
      </p>
      <button
        v-if="task.prompt.length > 60"
        class="prompt-toggle"
        @click="isPromptExpanded = !isPromptExpanded"
      >
        {{ isPromptExpanded ? '收起' : '展开' }}
      </button>
      <button class="prompt-copy" @click="copyPrompt">
        <CopyIcon :size="12" />
        <span>{{ copyLabel }}</span>
      </button>
    </div>

    <!-- 输入文件 -->
    <div v-if="task.input_files?.length" class="task-files">
      <Thumbnail
        v-for="file in task.input_files"
        :key="file.file_id"
        :file="file"
        size="small"
        @click="previewStore.openPreview(file)"
      />
    </div>

    <!-- 参数信息 -->
    <div class="task-params">
      <span class="mode-badge" :class="task.mode">{{ task.mode === 'image' ? '图片' : '视频' }}</span>
      <span class="param-model">{{ modelName }}</span>
      <span v-for="(val, key) in displayParams" :key="key" class="param-value">
        <span class="param-dot">·</span> {{ val }}
      </span>
    </div>

    <!-- 输出结果 -->
    <div class="task-results">
      <template v-if="task.output_files?.length">
        <div class="results-grid">
          <div
            v-for="file in task.output_files"
            :key="file.file_id"
            class="result-item"
            @click="previewStore.openPreview(file)"
          >
            <Thumbnail
              :file="file"
              show-download
              @click="previewStore.openPreview(file)"
            />
          </div>
        </div>
      </template>

      <template v-else-if="isLoading">
        <div class="status-loading">
          <div class="spinner" />
          <span class="status-text">{{ statusText }}</span>
          <button v-if="showCancel" class="cancel-btn" @click="$emit('cancel')">
            取消
          </button>
        </div>
      </template>

      <template v-else-if="isError">
        <div class="status-error">
          <span>生成失败 {{ task.error_code ? `(${task.error_code})` : '' }}</span>
        </div>
      </template>

      <template v-else-if="task.status === 'cancelled'">
        <div class="status-error">
          <span>已取消</span>
        </div>
      </template>
    </div>

    <!-- 操作栏 -->
    <div class="task-actions">
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
import { computed, ref } from 'vue'
import { RefreshCw as RefreshIcon, Copy as CopyIcon } from 'lucide-vue-next'
import dayjs from 'dayjs'
import { usePreviewStore } from '@/stores'
import Thumbnail from '@/components/Thumbnail.vue'
import type { TaskItem } from '@/types'

const props = defineProps<{
  task: TaskItem
  showReuse?: boolean
  showCancel?: boolean
}>()

defineEmits<{
  (e: 'reuse'): void
  (e: 'cancel'): void
}>()

const previewStore = usePreviewStore()

const isPromptExpanded = ref(false)
const copyLabel = ref('复制')

async function copyPrompt() {
  try {
    await navigator.clipboard.writeText(props.task.prompt)
    copyLabel.value = '已复制'
    setTimeout(() => {
      copyLabel.value = '复制'
    }, 1500)
  } catch {
    copyLabel.value = '失败'
    setTimeout(() => {
      copyLabel.value = '复制'
    }, 1500)
  }
}

const modelName = computed(() => {
  return props.task.model_name || props.task.model_id
})

const displayParams = computed(() => {
  const p = props.task.parameters || {}
  const result: Record<string, string> = {}
  if (p.aspectRatio) result['比例'] = p.aspectRatio
  else if (p.ratio) result['比例'] = p.ratio
  if (p.duration) result['时长'] = `${p.duration}s`
  if (p.size) result['尺寸'] = p.size
  if (p.output_format) result['格式'] = p.output_format
  if (p.resolution) result['分辨率'] = p.resolution
  if (p.fps) result['帧率'] = `${p.fps}fps`
  return result
})

const isLoading = computed(() =>
  ['pending', 'queued', 'running', 'downloading'].includes(props.task.status)
)

const isError = computed(() => props.task.status === 'failed')

const statusText = computed(() => {
  const map: Record<string, string> = {
    pending: '等待中...',
    queued: '排队中...',
    running: '生成中...',
    downloading: '下载结果中...',
  }
  return map[props.task.status] || props.task.status
})

function formatTime(t: string) {
  return dayjs(t).format('MM-DD HH:mm')
}
</script>

<style scoped>
.task-block {
  border-bottom: 1px solid #ffffff0f;
  padding: 16px 0;
  animation: slide-up 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.task-prompt {
  margin-bottom: 8px;
}

.prompt-text {
  color: var(--color-text-primary);
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.prompt-text:hover {
  color: var(--color-text-primary);
}

.prompt-text.expanded {
  -webkit-line-clamp: unset;
  display: block;
}

.prompt-toggle,
.prompt-copy {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-top: 4px;
  margin-right: 8px;
  padding: 2px 6px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--color-text-muted);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.prompt-toggle:hover,
.prompt-copy:hover {
  color: var(--color-text-secondary);
  background: #ffffff08;
}

.task-files {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.task-params {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}

.mode-badge {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
}

.mode-badge.image {
  color: var(--color-mode-image);
  background: #f59e0b1f;
}

.mode-badge.video {
  color: var(--color-accent);
  background: #6366f11f;
}

.param-model {
  color: var(--color-text-secondary);
  font-size: 11px;
}

.param-value {
  color: var(--color-text-muted);
  font-size: 11px;
}

.param-dot {
  color: var(--color-text-muted);
  font-size: 11px;
}

.task-results {
  min-height: 50px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
}

.result-item {
  aspect-ratio: 1;
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-bg-tertiary);
  position: relative;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.result-item:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.status-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff14;
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.status-text {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.cancel-btn {
  margin-left: auto;
  padding: 4px 10px;
  background: #ef44441a;
  border: none;
  border-radius: 6px;
  color: var(--color-error);
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.cancel-btn:hover {
  background: #ef444433;
}

.status-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  font-size: 13px;
  color: var(--color-error);
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.reuse-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--color-text-muted);
  font-size: 11px;
  cursor: pointer;
  transition: color 0.2s;
}

.reuse-btn:hover {
  color: var(--color-text-secondary);
  background: #ffffff08;
}

.task-time {
  margin-left: auto;
  font-size: 11px;
  color: var(--color-text-muted);
}
</style>
