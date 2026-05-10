<template>
  <div class="generate-page">
    <div class="generate-header">
      <button class="new-chat-btn" @click="resetSession">
        <PlusIcon :size="16" />
        <span>新建会话</span>
      </button>
    </div>

    <div class="generate-content" ref="contentRef">
      <TaskBlock
        v-for="task in taskStore.tasks"
        :key="task.platform_task_id"
        :task="task"
        @reuse="reuseTask(task)"
      />
    </div>

    <InputBar
      v-model:prompt="prompt"
      v-model:mode="selectedMode"
      v-model:model="selectedModel"
      v-model:params="parameters"
      v-model:files="uploadedFiles"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from 'lucide-vue-next'
import { useTaskStore } from '@/stores'
import type { TaskItem, TaskMode, TaskParameters, FileItem } from '@/types'
import InputBar from '@/components/InputBar.vue'
import TaskBlock from '@/components/TaskBlock.vue'

const taskStore = useTaskStore()
const contentRef = ref<HTMLElement>()

const prompt = ref('')
const selectedMode = ref<TaskMode>('image')
const selectedModel = ref('')
const parameters = ref<TaskParameters>({})
const uploadedFiles = ref<FileItem[]>([])

async function handleSubmit() {
  if (!prompt.value.trim()) {
    alert('请输入提示词')
    return
  }
  if (!selectedModel.value) {
    alert('请选择模型')
    return
  }

  const fileIds = uploadedFiles.value.map((f) => f.file_id)
  await taskStore.createTask(
    selectedMode.value,
    selectedModel.value,
    prompt.value,
    parameters.value,
    fileIds
  )

  // 清空输入
  prompt.value = ''
  uploadedFiles.value = []
}

function reuseTask(task: TaskItem) {
  selectedMode.value = task.mode
  selectedModel.value = task.model_id
  prompt.value = task.prompt
  parameters.value = task.parameters || {}
  // uploadedFiles 需要重新获取
}

function resetSession() {
  prompt.value = ''
  selectedMode.value = 'image'
  selectedModel.value = ''
  parameters.value = {}
  uploadedFiles.value = []
}

// 轮询进行中任务状态
onMounted(() => {
  const interval = setInterval(() => {
    taskStore.tasks.forEach((task) => {
      if (['pending', 'queued', 'running', 'downloading'].includes(task.status)) {
        taskStore.fetchTask(task.platform_task_id)
      }
    })
  }, 5000)

  return () => clearInterval(interval)
})
</script>

<style scoped>
.generate-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.generate-header {
  padding: 12px 20px;
  display: flex;
  justify-content: flex-start;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.generate-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px 200px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
