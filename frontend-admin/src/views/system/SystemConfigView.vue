<template>
  <div class="max-w-[900px]">
    <div class="mb-6">
      <h1 class="text-xl font-semibold text-txtp">系统配置</h1>
    </div>
    <div class="flex flex-col gap-6">
      <!-- API配置 -->
      <div class="bg-card border border-borderc rounded-card p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-base font-semibold text-txtp">API 配置</h2>
          <button class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed transition-colors" @click="openApiForm()">新增配置</button>
        </div>

        <!-- 新增/编辑表单 -->
        <div v-if="showApiForm" class="bg-active border border-borderc rounded-card p-5 mb-4">
          <h3 class="text-sm font-semibold mb-4 text-txtp">{{ editingApiId ? '编辑 API 配置' : '新增 API 配置' }}</h3>
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-txts">配置名称 <span class="text-danger">*</span></label>
              <input v-model="apiForm.name" placeholder="如：火山方舟主账号" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-txts">平台类型 <span class="text-danger">*</span></label>
              <select v-model="apiForm.platform" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors">
                <option value="volcengine_ark">火山方舟</option>
              </select>
            </div>
            <div class="flex flex-col gap-1.5 col-span-2">
              <label class="text-[13px] text-txts">API Key <span class="text-danger">*</span></label>
              <input v-model="apiForm.api_key" type="password" placeholder="sk-xxx..." class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
            </div>
            <div class="flex flex-col gap-1.5 col-span-2">
              <label class="text-[13px] text-txts">Base URL</label>
              <input v-model="apiForm.base_url" placeholder="https://ark.cn-beijing.volces.com/api/v3" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-txts">总并发限制</label>
              <input v-model.number="apiForm.total_concurrency" type="number" min="1" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="flex items-center gap-2 text-sm text-txtp cursor-pointer">
                <input v-model="apiForm.is_active" type="checkbox" class="accent-accent w-4 h-4 cursor-pointer" />
                启用该配置
              </label>
            </div>
          </div>
          <div class="flex justify-end gap-3">
            <button class="px-4 h-9 bg-active border border-borderc rounded-btn text-txts text-[13px] cursor-pointer hover:bg-hover transition-colors" @click="closeApiForm">取消</button>
            <button class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed transition-colors" @click="saveApi" :disabled="savingApi">
              {{ savingApi ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <div v-for="api in apiConfigs" :key="api.id" class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <div class="flex flex-col gap-0.5 flex-1">
              <span class="text-sm font-medium text-txtp">{{ api.name }}</span>
              <span class="text-xs text-txtm">{{ api.base_url }}</span>
            </div>
            <div class="flex items-center gap-3 mx-4">
              <span class="px-2 py-0.5 rounded text-xs" :class="api.is_active ? 'bg-success/15 text-success' : 'bg-txtm/15 text-txtm'">
                {{ api.is_active ? '启用' : '禁用' }}
              </span>
              <span class="text-xs text-txts">并发: {{ api.total_concurrency }}</span>
            </div>
            <div class="flex gap-2">
              <button class="px-2 py-1 bg-transparent border-none text-accent text-[13px] cursor-pointer hover:text-accent-hover transition-colors" @click="openApiForm(api)">编辑</button>
              <button class="px-2 py-1 bg-transparent border-none text-danger text-[13px] cursor-pointer hover:text-danger/80 transition-colors" @click="deleteApi(api.id)">删除</button>
            </div>
          </div>
          <div v-if="apiConfigs.length === 0" class="text-center py-6 text-txtm text-sm">暂无 API 配置</div>
        </div>
      </div>

      <!-- 存储配置 -->
      <div class="bg-card border border-borderc rounded-card p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-base font-semibold text-txtp">存储配置</h2>
          <button class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed transition-colors" @click="saveStorage" :disabled="savingStorage">
            {{ savingStorage ? '保存中...' : '保存配置' }}
          </button>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">最大存储容量</label>
            <div class="flex gap-2">
              <input v-model.number="storageForm.max_storage_value" type="number" min="1" class="flex-1 h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
              <select v-model="storageForm.max_storage_unit" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors">
                <option value="GB">GB</option>
                <option value="TB">TB</option>
              </select>
            </div>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">文件保留时间（天）</label>
            <input v-model.number="storageForm.file_retention_days" type="number" min="1" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
          </div>
        </div>
      </div>

      <!-- 任务队列配置 -->
      <div class="bg-card border border-borderc rounded-card p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-base font-semibold text-txtp">任务队列配置</h2>
          <button class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed transition-colors" @click="saveTaskQueue" :disabled="savingTaskQueue">
            {{ savingTaskQueue ? '保存中...' : '保存配置' }}
          </button>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">默认轮询间隔（秒）</label>
            <input v-model.number="taskQueueForm.poll_interval" type="number" min="5" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">最大重试次数</label>
            <input v-model.number="taskQueueForm.max_retries" type="number" min="0" max="10" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">单用户最大并发任务</label>
            <input v-model.number="taskQueueForm.max_user_concurrent_tasks" type="number" min="1" max="10" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
          </div>
        </div>
      </div>

      <!-- TOS配置 -->
      <div class="bg-card border border-borderc rounded-card p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-base font-semibold text-txtp">TOS 对象存储配置</h2>
          <button class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed transition-colors" @click="saveTos" :disabled="savingTos">
            {{ savingTos ? '保存中...' : '保存配置' }}
          </button>
        </div>
        <p class="text-xs text-txtm mb-3">修改后将覆盖服务器环境变量中的 TOS 配置。</p>

        <!-- TOS 启用开关 -->
        <div class="flex items-center gap-3 mb-4">
          <button
            class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors cursor-pointer"
            :class="tosForm.enabled ? 'bg-accent' : 'bg-txtm/30'"
            @click="tosForm.enabled = !tosForm.enabled"
          >
            <span
              class="inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform"
              :class="tosForm.enabled ? 'translate-x-[18px]' : 'translate-x-[2px]'"
            />
          </button>
          <span class="text-sm text-txtp">{{ tosForm.enabled ? '已启用' : '已禁用' }}</span>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">Endpoint</label>
            <input v-model="tosForm.endpoint" placeholder="tos-cn-beijing.volces.com" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">Region</label>
            <input v-model="tosForm.region" placeholder="cn-beijing" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">Bucket <span class="text-danger">*</span></label>
            <input v-model="tosForm.bucket" placeholder="bucket-name" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">Access Key <span class="text-danger">*</span></label>
            <input v-model="tosForm.access_key" type="password" placeholder="AK..." class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">Secret Key <span class="text-danger">*</span></label>
            <input v-model="tosForm.secret_key" type="password" placeholder="SK..." class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import type { ApiConfig } from '@/types'

const apiConfigs = ref<ApiConfig[]>([])
const showApiForm = ref(false)
const editingApiId = ref<number | null>(null)
const savingApi = ref(false)
const savingTos = ref(false)
const savingStorage = ref(false)
const savingTaskQueue = ref(false)

const apiForm = ref({
  name: '',
  platform: 'volcengine_ark',
  api_key: '',
  base_url: 'https://ark.cn-beijing.volces.com/api/v3',
  total_concurrency: 5,
  is_active: true,
})

const storageForm = ref({
  max_storage_value: 100,
  max_storage_unit: 'GB',
  file_retention_days: 30,
})

const taskQueueForm = ref({
  poll_interval: 30,
  max_retries: 3,
  max_user_concurrent_tasks: 5,
})

const tosForm = ref({
  enabled: true,
  endpoint: '',
  region: '',
  bucket: '',
  access_key: '',
  secret_key: '',
})

async function fetchConfigs() {
  try {
    const res = await api.get('/admin/api-configs')
    apiConfigs.value = res.data
  } catch (e) {
    alert('获取 API 配置失败')
  }
}

async function fetchStorageConfig() {
  try {
    const res = await api.get('/admin/system-config/storage')
    const data = res.data.config_value || {}
    storageForm.value = {
      max_storage_value: data.max_storage_value ?? 100,
      max_storage_unit: data.max_storage_unit || 'GB',
      file_retention_days: data.file_retention_days ?? 30,
    }
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取存储配置失败')
  }
}

async function fetchTaskQueueConfig() {
  try {
    const res = await api.get('/admin/system-config/task_queue')
    const data = res.data.config_value || {}
    taskQueueForm.value = {
      poll_interval: data.poll_interval ?? 30,
      max_retries: data.max_retries ?? 3,
      max_user_concurrent_tasks: data.max_user_concurrent_tasks ?? 5,
    }
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取任务队列配置失败')
  }
}

async function fetchTosConfig() {
  try {
    const res = await api.get('/admin/system-config/tos')
    const data = res.data.config_value || {}
    tosForm.value = {
      enabled: data.enabled ?? true,
      endpoint: data.endpoint || '',
      region: data.region || '',
      bucket: data.bucket || '',
      access_key: data.access_key || '',
      secret_key: data.secret_key || '',
    }
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取 TOS 配置失败')
  }
}

async function saveStorage() {
  savingStorage.value = true
  try {
    await api.put('/admin/system-config/storage', {
      config_value: { ...storageForm.value },
      description: '存储配置',
    })
    alert('存储配置已保存')
  } catch (e: any) {
    alert(e.response?.data?.detail || '保存失败')
  } finally {
    savingStorage.value = false
  }
}

async function saveTaskQueue() {
  savingTaskQueue.value = true
  try {
    await api.put('/admin/system-config/task_queue', {
      config_value: { ...taskQueueForm.value },
      description: '任务队列配置',
    })
    alert('任务队列配置已保存')
  } catch (e: any) {
    alert(e.response?.data?.detail || '保存失败')
  } finally {
    savingTaskQueue.value = false
  }
}

async function saveTos() {
  if (tosForm.value.enabled) {
    if (!tosForm.value.bucket || !tosForm.value.access_key || !tosForm.value.secret_key) {
      alert('请填写 Bucket、Access Key 和 Secret Key')
      return
    }
  }
  savingTos.value = true
  try {
    await api.put('/admin/system-config/tos', {
      config_value: { ...tosForm.value },
      description: 'TOS对象存储配置',
    })
    alert('TOS 配置已保存')
  } catch (e: any) {
    alert(e.response?.data?.detail || '保存失败')
  } finally {
    savingTos.value = false
  }
}

function openApiForm(config?: ApiConfig) {
  if (config) {
    editingApiId.value = config.id
    apiForm.value = {
      name: config.name,
      platform: config.platform,
      api_key: config.api_key,
      base_url: config.base_url,
      total_concurrency: config.total_concurrency,
      is_active: config.is_active,
    }
  } else {
    editingApiId.value = null
    apiForm.value = {
      name: '',
      platform: 'volcengine_ark',
      api_key: '',
      base_url: 'https://ark.cn-beijing.volces.com/api/v3',
      total_concurrency: 5,
      is_active: true,
    }
  }
  showApiForm.value = true
}

function closeApiForm() {
  showApiForm.value = false
  editingApiId.value = null
}

async function saveApi() {
  if (!apiForm.value.name || !apiForm.value.api_key) {
    alert('请填写名称和 API Key')
    return
  }
  savingApi.value = true
  try {
    if (editingApiId.value) {
      await api.put(`/admin/api-configs/${editingApiId.value}`, apiForm.value)
    } else {
      await api.post('/admin/api-configs', apiForm.value)
    }
    closeApiForm()
    await fetchConfigs()
  } catch (e: any) {
    alert(e.response?.data?.detail || '保存失败')
  } finally {
    savingApi.value = false
  }
}

async function deleteApi(id: number) {
  if (!confirm('确定删除该 API 配置？')) return
  try {
    await api.delete(`/admin/api-configs/${id}`)
    await fetchConfigs()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  fetchConfigs()
  fetchStorageConfig()
  fetchTaskQueueConfig()
  fetchTosConfig()
})
</script>
