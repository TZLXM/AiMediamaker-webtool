import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TaskItem, TaskMode, TaskParameters, FileItem } from '@/types'
import api from '@/api'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<TaskItem[]>([])
  const currentTask = ref<TaskItem | null>(null)

  async function createTask(
    mode: TaskMode,
    modelId: string,
    prompt: string,
    parameters: TaskParameters,
    fileIds: string[]
  ) {
    const res = await api.post('/tasks/create', {
      mode,
      model_id: modelId,
      prompt,
      parameters,
      file_ids: fileIds,
    })
    const task = res.data as TaskItem
    tasks.value.unshift(task)
    return task
  }

  async function fetchTask(platformTaskId: string) {
    const res = await api.get(`/tasks/${platformTaskId}`)
    const task = res.data as TaskItem
    const idx = tasks.value.findIndex((t) => t.platform_task_id === platformTaskId)
    if (idx >= 0) {
      tasks.value[idx] = task
    }
    return task
  }

  async function cancelTask(platformTaskId: string) {
    await api.post(`/tasks/${platformTaskId}/cancel`)
    const idx = tasks.value.findIndex((t) => t.platform_task_id === platformTaskId)
    if (idx >= 0) {
      tasks.value[idx].status = 'cancelled'
    }
  }

  async function fetchHistory(params?: { mode?: string; search?: string; start_date?: string; end_date?: string; page?: number; page_size?: number }) {
    const res = await api.get('/tasks/history/list', { params })
    return res.data as TaskItem[]
  }

  async function fetchAssets(params?: { file_type?: string; search?: string; start_date?: string; end_date?: string; page?: number; page_size?: number }) {
    const res = await api.get('/files/assets/list', { params })
    return res.data as FileItem[]
  }

  async function deleteFile(fileId: string) {
    await api.delete(`/files/${fileId}`)
  }

  function addOrUpdateTask(task: TaskItem) {
    const idx = tasks.value.findIndex((t) => t.platform_task_id === task.platform_task_id)
    if (idx >= 0) {
      tasks.value[idx] = task
    } else {
      tasks.value.unshift(task)
    }
  }

  function clearTasks() {
    tasks.value = []
    currentTask.value = null
  }

  return {
    tasks,
    currentTask,
    createTask,
    fetchTask,
    cancelTask,
    fetchHistory,
    fetchAssets,
    deleteFile,
    addOrUpdateTask,
    clearTasks,
  }
})
