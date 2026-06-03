<template>
  <div class="generate-page">
    <div class="top-bar">
      <button class="new-session-btn" @click="resetSession">
        <PlusIcon :size="16" />
        <span>新建会话</span>
      </button>
    </div>

    <div class="tasks-container">
      <!-- 空状态 -->
      <div v-if="taskStore.tasks.length === 0" class="empty-state">
        <div class="empty-icon">
          <SparklesIcon :size="32" />
        </div>
        <h3>开始你的第一次创作</h3>
        <p>输入提示词，选择模型和参数，即可生成图片或视频</p>
        <div class="quick-actions">
          <button class="quick-btn" @click="quickStart('image')">
            <ImageIcon :size="16" />
            <span>生成图片</span>
          </button>
          <button class="quick-btn" @click="quickStart('video')">
            <VideoIcon :size="16" />
            <span>生成视频</span>
          </button>
        </div>
      </div>

      <!-- 任务列表 -->
      <TransitionGroup v-else name="task-list" tag="div" class="tasks-list">
        <TaskBlock
          v-for="task in taskStore.tasks"
          :key="task.platform_task_id"
          :task="task"
          show-reuse
          show-cancel
          @reuse="reuseTask(task)"
          @cancel="cancelTask(task.platform_task_id)"
        />
      </TransitionGroup>
    </div>

    <InputBar
      ref="inputBarRef"
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
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus as PlusIcon, Sparkles as SparklesIcon, Image as ImageIcon, Video as VideoIcon } from 'lucide-vue-next'
import { useTaskStore } from '@/stores'
import type { TaskItem, TaskMode, TaskParameters, FileItem } from '@/types'
import InputBar from '@/components/InputBar.vue'
import TaskBlock from '@/components/TaskBlock.vue'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const inputBarRef = ref<InstanceType<typeof InputBar>>()

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
  try {
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
  } catch (e: any) {
    const detail = e.response?.data?.detail
    const message = typeof detail === 'string' ? detail : e.message
    alert(`创建任务失败: ${message || '请检查网络或稍后重试'}`)
  }
}

function reuseTask(task: TaskItem) {
  selectedMode.value = task.mode
  parameters.value = task.parameters || {}
  selectedModel.value = task.model_id
  prompt.value = task.prompt
  // 复用输入文件
  if (task.input_files?.length) {
    uploadedFiles.value = [...task.input_files]
  } else {
    uploadedFiles.value = []
  }
}

function resetSession() {
  prompt.value = ''
  selectedMode.value = 'image'
  selectedModel.value = ''
  parameters.value = {}
  uploadedFiles.value = []
  taskStore.tasks = []
}

function quickStart(mode: TaskMode) {
  selectedMode.value = mode
  prompt.value = ''
  nextTick(() => {
    inputBarRef.value?.focus()
  })
}

async function cancelTask(platformTaskId: string) {
  if (!confirm('确定要取消该任务吗？')) return
  await taskStore.cancelTask(platformTaskId)
}

async function loadAndReuseTask(taskId: string) {
  try {
    const task = await taskStore.fetchTask(taskId)
    if (task) {
      reuseTask(task)
    }
  } catch {
    // 任务不存在或已删除，忽略
  }
}

// 监听 query 参数中的复用任务
watch(
  () => route.query.reuse_task_id,
  (taskId) => {
    if (taskId && typeof taskId === 'string') {
      loadAndReuseTask(taskId)
      // 清除 query 参数，避免刷新时重复填充
      router.replace({ path: '/generate', query: {} })
    }
  },
  { immediate: true }
)

// 轮询进行中任务状态
let pollInterval: ReturnType<typeof setInterval>
onMounted(() => {
  pollInterval = setInterval(() => {
    taskStore.tasks.forEach((task) => {
      if (['pending', 'queued', 'running', 'downloading'].includes(task.status)) {
        taskStore.fetchTask(task.platform_task_id)
      }
    })
  }, 5000)
})

onUnmounted(() => {
  clearInterval(pollInterval)
})
</script>

<style scoped>
.generate-page {
  width: 100%;
  min-height: 100%;
  padding-bottom: 240px;
  position: relative;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 40;
  padding: 16px 24px 8px;
  background: linear-gradient(to bottom, var(--color-bg-primary) 60%, transparent);
}

.new-session-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #ffffff0a;
  border: 1px solid #ffffff0f;
  border-radius: 10px;
  color: var(--color-text-secondary);
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.new-session-btn:hover {
  color: var(--color-text-primary);
  background: #ffffff14;
  border-color: #ffffff1a;
}

.tasks-container {
  padding: 0 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
  padding: 40px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: linear-gradient(135deg, #6366f11f, #a855f71f);
  color: var(--color-accent);
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.empty-state p {
  color: var(--color-text-muted);
  max-width: 360px;
  margin: 0 0 24px;
  font-size: 14px;
  line-height: 1.6;
}

.quick-actions {
  display: flex;
  gap: 12px;
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  border: 1px solid #ffffff0f;
  border-radius: 12px;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  border-color: #ffffff1a;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  max-width: 960px;
  margin: 0 auto;
}

.task-list-move,
.task-list-enter-active,
.task-list-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.task-list-enter-from,
.task-list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
.task-list-leave-active {
  position: absolute;
}
</style>
