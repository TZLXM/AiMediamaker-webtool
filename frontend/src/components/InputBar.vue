<template>
  <div class="input-bar">
    <div v-if="uploadedFiles.length > 0" class="uploaded-files-row">
      <div
        v-for="(file, idx) in uploadedFiles"
        :key="file.file_id"
        class="file-thumb"
      >
        <img v-if="file.file_type === 'image'" :src="file.url" />
        <video v-else-if="file.file_type === 'video'" :src="file.url" />
        <div v-else class="audio-thumb">Audio</div>
        <button class="file-remove" @click="removeFile(idx)">
          <XIcon :size="12" />
        </button>
      </div>
    </div>

    <div class="prompt-area">
      <div
        ref="promptRef"
        class="prompt-editor"
        contenteditable
        @input="onInput"
        @keydown="onKeydown"
        placeholder="输入提示词，使用 @ 引用文件..."
      />
    </div>

    <div class="action-bar">
      <div class="action-left">
        <button class="action-btn" @click="showModeSelect = !showModeSelect">
          {{ modeLabel }}
        </button>
        <button class="action-btn" @click="showModelSelect = !showModelSelect">
          {{ selectedModelName || '选择模型' }}
        </button>
        <button class="action-btn" @click="showParams = !showParams">
          生成参数
        </button>
      </div>
      <button class="generate-btn" :disabled="!canSubmit" @click="submit">
        <SparklesIcon :size="16" />
        <span>生成</span>
      </button>
    </div>

    <!-- Mode Dropdown -->
    <div v-if="showModeSelect" class="dropdown-menu">
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

    <!-- Model Dropdown -->
    <div v-if="showModelSelect" class="dropdown-menu">
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

    <!-- Params Panel -->
    <div v-if="showParams" class="params-panel">
      <div
        v-for="param in currentModelParams"
        :key="param.key"
        class="param-field"
      >
        <label>{{ param.label }}</label>
        <select v-if="param.type === 'select'" v-model="params[param.key]">
          <option v-for="opt in param.options" :key="String(opt.value)" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
        <input
          v-else-if="param.type === 'number'"
          :value="params[param.key]"
          @input="(e) => { params[param.key] = Number((e.target as HTMLInputElement).value) }"
          type="number"
          :min="param.min"
          :max="param.max"
        />
        <label v-else-if="param.type === 'boolean'" class="checkbox">
          <input
            :checked="params[param.key]"
            @change="(e) => { params[param.key] = (e.target as HTMLInputElement).checked }"
            type="checkbox"
          />
          {{ param.description }}
        </label>
      </div>
    </div>

    <!-- @ File Picker -->
    <div v-if="showFilePicker" class="file-picker">
      <div
        v-for="(file, idx) in availableFiles"
        :key="file.file_id"
        class="file-picker-item"
        @click="insertFileRef(file, idx)"
      >
        {{ fileTypeLabel(file.file_type) }}{{ idx + 1 }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Sparkles as SparklesIcon, X as XIcon } from 'lucide-vue-next'
import api from '@/api'
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

const promptRef = ref<HTMLElement>()
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
const showFilePicker = ref(false)
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

const canSubmit = computed(() => !!props.prompt.trim() && !!selectedModel.value)

async function loadModels() {
  const res = await api.get('/models/list', { params: { mode: selectedMode.value } })
  models.value = res.data
}

function selectMode(mode: TaskMode) {
  selectedMode.value = mode
  selectedModel.value = ''
  showModeSelect.value = false
  loadModels()
}

function selectModel(modelId: string) {
  selectedModel.value = modelId
  showModelSelect.value = false
}

function submit() {
  emit('submit')
}

function removeFile(idx: number) {
  uploadedFiles.value.splice(idx, 1)
}

function onInput(e: Event) {
  const text = (e.target as HTMLElement).innerText
  emit('update:prompt', text)
  showFilePicker.value = text.endsWith('@')
}

function onKeydown(e: KeyboardEvent) {
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
  const text = promptRef.value?.innerText || ''
  const newText = text.slice(0, -1) + `@${fileTypeLabel(file.file_type)}${idx + 1} `
  if (promptRef.value) promptRef.value.innerText = newText
  emit('update:prompt', newText)
  showFilePicker.value = false
}

watch(selectedMode, loadModels, { immediate: true })
</script>

<style scoped>
.input-bar {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  z-index: 10;
}

.uploaded-files-row {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.file-thumb {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  background: var(--bg-tertiary);
}

.file-thumb img,
.file-thumb video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.audio-thumb {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: var(--text-muted);
}

.file-remove {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.prompt-area {
  margin-bottom: 10px;
}

.prompt-editor {
  min-height: 40px;
  max-height: 160px;
  overflow-y: auto;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.5;
  outline: none;
  white-space: pre-wrap;
  word-break: break-word;
}

.prompt-editor:empty::before {
  content: attr(placeholder);
  color: var(--text-muted);
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-left {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.generate-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: var(--accent);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.generate-btn:hover {
  background: var(--accent-hover);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dropdown-menu {
  position: absolute;
  bottom: 100%;
  left: 14px;
  margin-bottom: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  min-width: 140px;
  z-index: 20;
}

.dropdown-item {
  padding: 10px 14px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.dropdown-item:hover,
.dropdown-item.active {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.params-panel {
  position: absolute;
  bottom: 100%;
  left: 14px;
  margin-bottom: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px;
  min-width: 220px;
  z-index: 20;
}

.param-field {
  margin-bottom: 10px;
}

.param-field label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.param-field select,
.param-field input[type='number'] {
  width: 100%;
  padding: 6px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}

.param-field .checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.file-picker {
  position: absolute;
  bottom: 100%;
  left: 14px;
  margin-bottom: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  min-width: 140px;
  z-index: 20;
}

.file-picker-item {
  padding: 10px 14px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.file-picker-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>
