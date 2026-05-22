<template>
  <div
    class="input-float"
    :class="{ 'drag-over': isDragOver }"
    @dragover.prevent="isDragOver = true"
    @dragleave.prevent="isDragOver = false"
    @drop.prevent="handleDrop"
  >
    <!-- 已上传文件缩略图 -->
    <div v-if="uploadedFiles.length > 0" class="uploaded-files-row">
      <div
        v-for="(file, idx) in uploadedFiles"
        :key="file.file_id"
        class="file-thumb"
      >
        <Thumbnail
          :file="file"
          size="small"
          show-delete
          @delete="removeFile(idx)"
        />
      </div>
    </div>

    <!-- 提示词输入 -->
    <div class="prompt-area">
      <textarea
        ref="promptRef"
        v-model="promptText"
        class="prompt-input"
        placeholder="输入提示词，使用 @ 引用文件..."
        rows="1"
        @input="onInput"
        @keydown="onKeydown"
      />

      <!-- @ 文件引用面板 -->
      <div v-if="showFilePicker" class="mention-panel">
        <div class="mention-header">引用文件</div>
        <div
          v-for="(file, idx) in availableFiles"
          :key="file.file_id"
          class="mention-item"
          :class="{ highlighted: highlightIndex === idx }"
          @click="insertFileRef(file, idx)"
        >
          <ImageIcon v-if="file.file_type === 'image'" :size="14" />
          <VideoIcon v-else-if="file.file_type === 'video'" :size="14" />
          <MusicIcon v-else :size="14" />
          {{ fileTypeLabel(file.file_type) }}{{ idx + 1 }}
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <!-- 模式选择 -->
        <div class="select-wrapper">
          <button
            class="pill-btn mode-pill"
            :class="{ active: showModeSelect }"
            @click="showModeSelect = !showModeSelect"
          >
            <ImageIcon v-if="selectedMode === 'image'" :size="13" />
            <VideoIcon v-else :size="13" />
            <span>{{ modeLabel }}</span>
            <ChevronDownIcon :size="11" />
          </button>
          <div v-if="showModeSelect" class="dropdown-panel">
            <div
              v-for="m in modes"
              :key="m.value"
              class="dropdown-item"
              :class="{ active: selectedMode === m.value }"
              @click="selectMode(m.value)"
            >
              {{ m.label }}
            </div>
          </div>
        </div>

        <!-- 模型选择 -->
        <div class="select-wrapper">
          <button
            class="pill-btn"
            :class="{ active: showModelSelect }"
            @click="showModelSelect = !showModelSelect"
          >
            <span>{{ selectedModelName || '选择模型' }}</span>
            <ChevronDownIcon :size="11" />
          </button>
          <div v-if="showModelSelect" class="dropdown-panel">
            <div
              v-for="model in filteredModels"
              :key="model.model_id"
              class="dropdown-item"
              :class="{ active: selectedModel === model.model_id }"
              @click="selectModel(model.model_id)"
            >
              {{ model.name }}
            </div>
          </div>
        </div>

        <!-- 参数选择 -->
        <div v-if="currentModel" class="select-wrapper">
          <button
            class="pill-btn param-pill"
            :class="{ active: showParams }"
            @click="showParams = !showParams"
          >
            <span class="ratio-icon">{{ ratioIcon }}</span>
            <span>{{ ratioLabel }}</span>
            <template v-if="resolutionLabel">
              <span class="param-sep">|</span>
              <span>{{ resolutionLabel }}</span>
            </template>
            <ChevronDownIcon :size="11" />
          </button>
          <div v-if="showParams && currentModel" class="dropdown-panel unified-params">
            <!-- 比例选择：固定选项网格（始终显示，对齐参考实现） -->
            <div class="param-section">
              <label>选择比例</label>
              <div class="ratio-grid">
                <button
                  v-for="opt in fixedRatioOptions"
                  :key="opt.value"
                  class="ratio-btn"
                  :class="{ active: ratioValue === opt.value }"
                  @click="setRatioParam(opt.value)"
                >
                  <div class="ratio-shape">
                    <div
                      class="ratio-inner"
                      :style="getRatioStyle(opt.value)"
                    />
                  </div>
                  <span>{{ opt.label }}</span>
                </button>
              </div>
            </div>

            <!-- 分辨率选择：按钮组 -->
            <div v-if="resolutionParam" class="param-section">
              <label>选择分辨率</label>
              <div class="res-options">
                <button
                  v-for="opt in resolutionParam.options"
                  :key="String(opt.value)"
                  class="res-btn"
                  :class="{ active: params[resolutionParam.key] === opt.value }"
                  @click="setParam(resolutionParam.key, opt.value)"
                >
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- 其他参数 -->
            <div
              v-for="param in otherParams"
              :key="param.key"
              class="param-section"
            >
              <label>{{ param.label }}</label>
              <div v-if="param.type === 'select' && param.options" class="res-options">
                <button
                  v-for="opt in param.options"
                  :key="String(opt.value)"
                  class="res-btn"
                  :class="{ active: params[param.key] === opt.value }"
                  @click="setParam(param.key, opt.value)"
                >
                  {{ opt.label }}
                </button>
              </div>
              <select
                v-else-if="param.type === 'select' && param.options"
                :value="params[param.key]"
                @change="(e) => setParam(param.key, (e.target as HTMLSelectElement).value)"
              >
                <option
                  v-for="opt in param.options"
                  :key="String(opt.value)"
                  :value="opt.value"
                >
                  {{ opt.label }}
                </option>
              </select>
              <input
                v-else-if="param.type === 'number'"
                :value="params[param.key]"
                type="number"
                :min="param.min"
                :max="param.max"
                @input="(e) => setParam(param.key, Number((e.target as HTMLInputElement).value))"
              />
              <label v-else-if="param.type === 'boolean'" class="checkbox">
                <input
                  :checked="params[param.key]"
                  type="checkbox"
                  @change="(e) => setParam(param.key, (e.target as HTMLInputElement).checked)"
                />
                {{ param.description || param.label }}
              </label>
            </div>
          </div>
        </div>

        <!-- 时长选择（视频模式） -->
        <div v-if="selectedMode === 'video' && durationOptions.length > 0" class="select-wrapper">
          <button
            class="pill-btn"
            :class="{ active: showDurationSelect }"
            @click="showDurationSelect = !showDurationSelect"
          >
            <ClockIcon :size="13" />
            <span>{{ durationLabel }}</span>
            <ChevronDownIcon :size="11" />
          </button>
          <div v-if="showDurationSelect" class="dropdown-panel">
            <div
              v-for="opt in durationOptions"
              :key="opt.value"
              class="dropdown-item"
              :class="{ active: params.duration === opt.value }"
              @click="setParam('duration', opt.value)"
            >
              {{ opt.label }}
            </div>
          </div>
        </div>

        <!-- 上传按钮 -->
        <button class="pill-btn upload-btn" title="上传文件" @click="fileInputRef?.click()">
          <PaperclipIcon :size="13" />
        </button>
        <input
          ref="fileInputRef"
          type="file"
          class="hidden-input"
          multiple
          accept="image/*,video/*,audio/*"
          @change="handleFileSelect"
        />
      </div>

      <!-- 生成按钮 -->
      <button
        class="generate-btn"
        :disabled="!canSubmit || isUploading"
        :title="isUploading ? '文件上传中...' : '生成'"
        @click="submit"
      >
        <SparklesIcon :size="15" />
      </button>
    </div>

    <!-- 上传进度 -->
    <div v-if="isUploading" class="upload-progress">
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }" />
      </div>
      <span class="progress-text">上传中 {{ uploadProgress }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import {
  Sparkles as SparklesIcon,
  Paperclip as PaperclipIcon,
  Image as ImageIcon,
  Video as VideoIcon,
  Music as MusicIcon,
  ChevronDown as ChevronDownIcon,
  Clock as ClockIcon,
} from 'lucide-vue-next'
import api from '@/api'
import Thumbnail from '@/components/Thumbnail.vue'
import type { TaskMode, TaskParameters, FileItem, ModelInfo } from '@/types'

const props = defineProps<{
  prompt: string
  mode: TaskMode
  model: string
  params: TaskParameters
  files: FileItem[]
}>()

const emit = defineEmits<{
  (e: 'update:prompt', value: string): void
  (e: 'update:mode', value: TaskMode): void
  (e: 'update:model', value: string): void
  (e: 'update:params', value: TaskParameters): void
  (e: 'update:files', value: FileItem[]): void
  (e: 'submit'): void
}>()

const promptRef = ref<HTMLTextAreaElement>()
const fileInputRef = ref<HTMLInputElement>()
const promptText = ref(props.prompt)
const isDragOver = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)

const uploadedFiles = computed({
  get: () => props.files,
  set: (v) => emit('update:files', v),
})
const selectedMode = computed({
  get: () => props.mode,
  set: (v) => emit('update:mode', v),
})
const selectedModel = computed({
  get: () => props.model,
  set: (v) => emit('update:model', v),
})
const params = computed({
  get: () => props.params,
  set: (v) => emit('update:params', v),
})

const showModeSelect = ref(false)
const showModelSelect = ref(false)
const showParams = ref(false)
const showDurationSelect = ref(false)
const showFilePicker = ref(false)
const highlightIndex = ref(0)
const models = ref<ModelInfo[]>([])

const modes = [
  { value: 'image' as TaskMode, label: '图片生成' },
  { value: 'video' as TaskMode, label: '视频生成' },
]

const modeLabel = computed(() => modes.find((m) => m.value === selectedMode.value)?.label || '模式')

const filteredModels = computed(() =>
  models.value.filter((m) => m.mode === selectedMode.value)
)

const selectedModelName = computed(() =>
  models.value.find((m) => m.model_id === selectedModel.value)?.name
)

const currentModelParams = computed(() =>
  models.value.find((m) => m.model_id === selectedModel.value)?.parameters || []
)

const currentModel = computed(() =>
  models.value.find((m) => m.model_id === selectedModel.value)
)

const canSubmit = computed(() => !!promptText.value.trim() && !!selectedModel.value)

// 固定比例选项（和参考实现一致）
const fixedRatioOptions = [
  { value: '智能', label: '智能' },
  { value: '21:9', label: '21:9' },
  { value: '16:9', label: '16:9' },
  { value: '3:2', label: '3:2' },
  { value: '4:3', label: '4:3' },
  { value: '1:1', label: '1:1' },
  { value: '3:4', label: '3:4' },
  { value: '2:3', label: '2:3' },
  { value: '9:16', label: '9:16' },
]

// 比例参数的 key（支持 aspectRatio 或 ratio）
const ratioParamKey = computed(() => {
  return currentModelParams.value.find((p) => p.key === 'aspectRatio' || p.key === 'ratio')?.key || 'aspectRatio'
})

// 当前比例值（显示用，adaptive/null 映射为 '智能'）
const ratioValue = computed(() => {
  const val = params.value[ratioParamKey.value]
  if (val === 'adaptive' || val == null) return '智能'
  return String(val)
})

// 比例图形符号（▭横屏 ▯竖屏 □正方形 ◻自适应）
const ratioIcon = computed(() => {
  const val = ratioValue.value
  if (val === '智能') return '◻'
  const parts = val.split(':')
  if (parts.length !== 2) return '◻'
  const w = parseInt(parts[0])
  const h = parseInt(parts[1])
  if (w > h) return '▭'
  if (w < h) return '▯'
  return '□'
})

// 比例文字标签
const ratioLabel = computed(() => ratioValue.value)

// 分辨率参数
const resolutionParam = computed(() => {
  return currentModelParams.value.find((p) => p.key === 'resolution') || null
})

// 分辨率标签
const resolutionLabel = computed(() => {
  const res = params.value.resolution
  if (!res) return ''
  if (res === '2K') return '高清 2K'
  if (res === '4K') return '超清 4K'
  return res
})

// 其他参数（过滤掉比例、分辨率、时长）
const otherParams = computed(() => {
  return currentModelParams.value.filter(
    (p) => p.key !== 'aspectRatio' && p.key !== 'ratio' && p.key !== 'resolution' && p.key !== 'duration'
  )
})

// 固定时长选项（和参考实现一致）
const fixedDurationOptions = [
  { value: -1, label: '自动' },
  { value: 4, label: '4秒' },
  { value: 5, label: '5秒' },
  { value: 6, label: '6秒' },
  { value: 8, label: '8秒' },
  { value: 10, label: '10秒' },
  { value: 15, label: '15秒' },
]

// 时长选项
const durationOptions = computed(() => fixedDurationOptions)

// 时长标签
const durationLabel = computed(() => {
  const dur = params.value.duration
  if (dur == null) return '5秒'
  const opt = fixedDurationOptions.find((o) => o.value === dur)
  return opt?.label || `${dur}秒`
})

// 自动调整 textarea 高度
function autoResize() {
  nextTick(() => {
    const el = promptRef.value
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 160) + 'px'
  })
}

watch(promptText, (val) => {
  emit('update:prompt', val)
  autoResize()
})

watch(() => props.prompt, (val) => {
  if (val !== promptText.value) {
    promptText.value = val
    autoResize()
  }
})

async function loadModels() {
  const res = await api.get('/models/list', { params: { mode: selectedMode.value } })
  models.value = res.data
}

function selectMode(mode: TaskMode) {
  selectedMode.value = mode
  selectedModel.value = ''
  params.value = {}
  showModeSelect.value = false
  // 过滤掉不兼容的文件
  filterIncompatibleFiles()
  loadModels()
}

function selectModel(modelId: string) {
  selectedModel.value = modelId
  showModelSelect.value = false
  const model = models.value.find((m) => m.model_id === modelId)
  if (model) {
    const defaults: Record<string, any> = {}
    for (const param of model.parameters) {
      if (param.default !== undefined) {
        defaults[param.key] = param.default
      }
    }
    // 确保比例参数有默认值（adaptive）
    const ratioKey = model.parameters.find((p) => p.key === 'aspectRatio' || p.key === 'ratio')?.key
    if (ratioKey && defaults[ratioKey] == null) {
      defaults[ratioKey] = 'adaptive'
    }
    params.value = defaults
    // 过滤掉不兼容的文件
    filterIncompatibleFiles()
  }
}

function setRatioParam(value: string) {
  const key = ratioParamKey.value
  const storedValue = value === '智能' ? 'adaptive' : value
  params.value = { ...params.value, [key]: storedValue }
}

function setParam(key: string, value: any) {
  params.value = { ...params.value, [key]: value }
}

function submit() {
  if (!canSubmit.value || isUploading.value) return
  emit('submit')
}

function removeFile(idx: number) {
  const newFiles = [...uploadedFiles.value]
  newFiles.splice(idx, 1)
  uploadedFiles.value = newFiles
}

function onInput() {
  showFilePicker.value = promptText.value.endsWith('@')
  highlightIndex.value = 0
}

function onKeydown(e: KeyboardEvent) {
  if (showFilePicker.value) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      highlightIndex.value = (highlightIndex.value + 1) % availableFiles.value.length
      return
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      highlightIndex.value = (highlightIndex.value - 1 + availableFiles.value.length) % availableFiles.value.length
      return
    }
    if (e.key === 'Enter') {
      e.preventDefault()
      const file = availableFiles.value[highlightIndex.value]
      if (file) insertFileRef(file, highlightIndex.value)
      return
    }
    if (e.key === 'Escape') {
      showFilePicker.value = false
      return
    }
  }
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    if (canSubmit.value) submit()
  }
}

const availableFiles = computed(() => uploadedFiles.value)

function fileTypeLabel(t: string) {
  return t === 'image' ? '图片' : t === 'video' ? '视频' : '音频'
}

function insertFileRef(file: FileItem, idx: number) {
  const prefix = promptText.value.slice(0, -1)
  const newText = prefix + `@${fileTypeLabel(file.file_type)}${idx + 1} `
  promptText.value = newText
  showFilePicker.value = false
  nextTick(() => promptRef.value?.focus())
}

// 文件类型校验
function isFileTypeAllowed(fileType: string): boolean {
  const supported = currentModel.value?.supported_input_types || []
  if (supported.length === 0) return true
  return supported.includes(fileType)
}

function filterIncompatibleFiles() {
  const compatible = uploadedFiles.value.filter((f) => isFileTypeAllowed(f.file_type))
  if (compatible.length !== uploadedFiles.value.length) {
    uploadedFiles.value = compatible
  }
}

// 上传文件
async function uploadFiles(files: FileList | null) {
  if (!files || files.length === 0) return
  isUploading.value = true
  uploadProgress.value = 0

  const newFiles: FileItem[] = []
  const total = files.length

  for (let i = 0; i < total; i++) {
    const file = files[i]
    const fileType = file.type.startsWith('image/')
      ? 'image'
      : file.type.startsWith('video/')
      ? 'video'
      : file.type.startsWith('audio/')
      ? 'audio'
      : null

    if (!fileType) {
      alert(`不支持的文件类型: ${file.name}`)
      continue
    }

    if (!isFileTypeAllowed(fileType)) {
      alert(`当前模型不支持 ${fileType} 类型文件: ${file.name}`)
      continue
    }

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await api.post('/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round(
            ((progressEvent.loaded / (progressEvent.total || 1)) + i) / total * 100
          )
          uploadProgress.value = Math.min(percent, 99)
        },
      })
      newFiles.push(res.data)
    } catch (e: any) {
      alert(`上传失败: ${file.name} - ${e.response?.data?.detail || e.message}`)
    }
  }

  if (newFiles.length > 0) {
    uploadedFiles.value = [...uploadedFiles.value, ...newFiles]
  }

  uploadProgress.value = 100
  setTimeout(() => {
    isUploading.value = false
    uploadProgress.value = 0
  }, 300)
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  uploadFiles(input.files)
  input.value = ''
}

function handleDrop(e: DragEvent) {
  isDragOver.value = false
  uploadFiles(e.dataTransfer?.files || null)
}

// 比例图形样式（在 28x18 容器内按比例显示）
function getRatioStyle(ratio: string) {
  if (ratio === '智能') return ''
  const parts = ratio.split(':')
  if (parts.length !== 2) return ''
  const w = parseInt(parts[0])
  const h = parseInt(parts[1])
  if (isNaN(w) || isNaN(h) || h === 0) return ''
  const containerW = 28
  const containerH = 18
  let rw = containerW
  let rh = containerH
  if (w / h > containerW / containerH) {
    rh = (containerW * h) / w
  } else {
    rw = (containerH * w) / h
  }
  return `width:${rw}px;height:${rh}px`
}

watch(selectedMode, loadModels, { immediate: true })
</script>

<style scoped>
.input-float {
  position: fixed;
  bottom: 20px;
  left: calc(50vw + 36px);
  transform: translateX(-50%);
  width: 92%;
  max-width: 1080px;
  background: #1e1e2a8c;
  -webkit-backdrop-filter: blur(24px) saturate(1.2);
  backdrop-filter: blur(24px) saturate(1.2);
  border: 1px solid var(--color-border);
  border-radius: 18px;
  padding: 18px 24px;
  z-index: 50;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
  box-shadow: 0 8px 40px #00000073, inset 0 1px #ffffff0a;
}

.input-float:focus-within {
  border-color: var(--color-border-hover);
}

.input-float.drag-over {
  background: #1e1e2abf;
  border-color: #6366f199;
  box-shadow: 0 8px 40px #00000080, 0 0 0 2px #6366f126, inset 0 1px #ffffff0f;
}

.uploaded-files-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ffffff0a;
}

.file-thumb {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
}

.prompt-area {
  margin-bottom: 6px;
  position: relative;
}

.prompt-input {
  width: 100%;
  min-height: 44px;
  max-height: 160px;
  padding: 2px 0;
  background: transparent;
  border: none;
  outline: none;
  color: var(--color-text-primary);
  font-family: inherit;
  font-size: 15px;
  line-height: 1.7;
  resize: none;
}

.prompt-input::placeholder {
  color: var(--color-text-muted);
}

.mention-panel {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 0;
  background: var(--color-bg-tertiary);
  border: 1px solid #ffffff1a;
  border-radius: 10px;
  min-width: 160px;
  padding: 6px 0;
  z-index: 60;
  box-shadow: 0 8px 32px #00000066;
}

.mention-header {
  padding: 4px 12px;
  font-size: 10px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 2px;
}

.mention-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.mention-item:hover,
.mention-item.highlighted {
  color: var(--color-text-primary);
  background: #ffffff0a;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid #ffffff0d;
}

.action-left {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.select-wrapper {
  position: relative;
}

.pill-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  background: #ffffff0a;
  border: 1px solid #ffffff0f;
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-family: inherit;
  font-size: 12px;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;
}

.pill-btn:hover {
  color: var(--color-text-primary);
  background: #ffffff14;
  border-color: #ffffff1a;
}

.pill-btn.active {
  color: var(--color-accent-hover);
  background: #6366f11a;
  border-color: #6366f14d;
}

.mode-pill {
  color: var(--color-accent-hover);
}

.param-pill .param-summary {
  font-size: 11px;
}

.upload-btn {
  width: 30px;
  height: 30px;
  padding: 5px;
  justify-content: center;
}

.hidden-input {
  display: none;
}

.generate-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #6366f1d9, #a855f7d9);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 12px #6366f140;
}

.generate-btn:hover {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  transform: scale(1.05);
  box-shadow: 0 4px 18px #6366f159;
}

.generate-btn:active {
  transform: scale(0.95);
}

.generate-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.dropdown-panel {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 0;
  background: var(--color-bg-tertiary);
  border: 1px solid #ffffff1a;
  border-radius: 10px;
  min-width: 170px;
  padding: 6px 0;
  z-index: 60;
  box-shadow: 0 8px 32px #00000066;
  animation: scale-in 0.15s ease;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  font-size: 13px;
  color: var(--color-text-secondary);
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.15s;
}

.dropdown-item:hover {
  color: var(--color-text-primary);
  background: #ffffff0a;
}

.dropdown-item.active {
  color: var(--color-accent);
  background: #6366f10f;
}

.unified-params {
  min-width: 320px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.param-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.param-section label {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 400;
}

.param-section select,
.param-section input[type='number'] {
  width: 100%;
  padding: 6px 10px;
  background: #ffffff0a;
  border: 1px solid #ffffff0f;
  border-radius: 6px;
  color: var(--color-text-primary);
  font-size: 13px;
  outline: none;
}

.param-section select:focus,
.param-section input[type='number']:focus {
  border-color: var(--color-accent);
}

.param-section .checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.ratio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  gap: 6px;
}

.ratio-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 8px 4px;
  background: #ffffff08;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-family: inherit;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.ratio-btn:hover {
  color: var(--color-text-primary);
  background: #ffffff0f;
}

.ratio-btn.active {
  color: var(--color-accent-hover);
  background: #6366f11f;
  border-color: #6366f166;
}

.ratio-shape {
  width: 28px;
  height: 18px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.ratio-inner {
  border: 1.5px solid;
  border-radius: 2px;
  opacity: 0.5;
}

.res-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.res-btn {
  flex: 1;
  min-width: 60px;
  padding: 8px 16px;
  background: #ffffff0a;
  border: 1px solid #ffffff0f;
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-family: inherit;
  font-size: 13px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.res-btn:hover {
  color: var(--color-text-primary);
  background: #ffffff14;
  border-color: #ffffff1a;
}

.res-btn.active {
  color: var(--color-accent-hover);
  background: #6366f11f;
  border-color: #6366f166;
}

.upload-progress {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-track {
  flex: 1;
  height: 3px;
  background: #ffffff0f;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-accent);
  border-radius: 2px;
  transition: width 0.2s;
}

.progress-text {
  font-size: 11px;
  color: var(--color-text-muted);
  white-space: nowrap;
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(4px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
