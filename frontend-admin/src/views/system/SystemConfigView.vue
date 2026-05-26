<template>
  <div class="max-w-[900px]">
    <div class="mb-6">
      <h1 class="text-xl font-semibold">系统配置</h1>
    </div>
    <div class="flex flex-col gap-6">
      <!-- API配置 -->
      <div class="bg-card border border-borderc rounded-card p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-base font-semibold">API 配置</h2>
          <button class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed" @click="openApiForm()">新增配置</button>
        </div>

        <!-- 新增/编辑表单 -->
        <div v-if="showApiForm" class="bg-active border border-borderc rounded-card p-5 mb-4">
          <h3 class="text-sm font-semibold mb-4 text-txtp">{{ editingApiId ? '编辑 API 配置' : '新增 API 配置' }}</h3>
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-txts">配置名称 <span class="text-danger">*</span></label>
              <input v-model="apiForm.name" placeholder="如：火山方舟主账号" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-txts">平台类型 <span class="text-danger">*</span></label>
              <select v-model="apiForm.platform" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent">
                <option value="volcengine_ark">火山方舟</option>
              </select>
            </div>
            <div class="flex flex-col gap-1.5 col-span-2">
              <label class="text-[13px] text-txts">API Key <span class="text-danger">*</span></label>
              <input v-model="apiForm.api_key" type="password" placeholder="sk-xxx..." class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
            </div>
            <div class="flex flex-col gap-1.5 col-span-2">
              <label class="text-[13px] text-txts">Base URL</label>
              <input v-model="apiForm.base_url" placeholder="https://ark.cn-beijing.volces.com/api/v3" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-[13px] text-txts">总并发限制</label>
              <input v-model.number="apiForm.total_concurrency" type="number" min="1" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="flex items-center gap-2 text-sm text-txtp cursor-pointer">
                <input v-model="apiForm.is_active" type="checkbox" />
                启用该配置
              </label>
            </div>
          </div>
          <div class="flex justify-end gap-3">
            <button class="px-4 h-9 bg-active border border-borderc rounded-btn text-txts text-[13px] cursor-pointer" @click="closeApiForm">取消</button>
            <button class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed" @click="saveApi" :disabled="savingApi">
              {{ savingApi ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <div v-for="api in apiConfigs" :key="api.id" class="flex items-center justify-between px-4 py-3 bg-active rounded-btn">
            <div class="flex flex-col gap-0.5 flex-1">
              <span class="text-sm font-medium">{{ api.name }}</span>
              <span class="text-xs text-txtm">{{ api.base_url }}</span>
            </div>
            <div class="flex items-center gap-3 mx-4">
              <span class="px-2 py-0.5 rounded text-xs" :class="api.is_active ? 'bg-success/15 text-success' : 'bg-txtm/15 text-txtm'">
                {{ api.is_active ? '启用' : '禁用' }}
              </span>
              <span class="text-xs text-txts">并发: {{ api.total_concurrency }}</span>
            </div>
            <div class="flex gap-2">
              <button class="px-2 py-1 bg-transparent border-none text-accent text-[13px] cursor-pointer" @click="openApiForm(api)">编辑</button>
              <button class="px-2 py-1 bg-transparent border-none text-danger text-[13px] cursor-pointer" @click="deleteApi(api.id)">删除</button>
            </div>
          </div>
          <div v-if="apiConfigs.length === 0" class="text-center py-6 text-txtm text-sm">暂无 API 配置</div>
        </div>
      </div>

      <!-- TOS配置 -->
      <div class="bg-card border border-borderc rounded-card p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-base font-semibold">TOS 对象存储配置</h2>
          <button class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed" @click="saveTos" :disabled="savingTos">
            {{ savingTos ? '保存中...' : '保存配置' }}
          </button>
        </div>
        <p class="text-xs text-txtm mb-3">修改后将覆盖服务器环境变量中的 TOS 配置。</p>
        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">Endpoint</label>
            <input v-model="tosForm.endpoint" placeholder="tos-cn-beijing.volces.com" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">Region</label>
            <input v-model="tosForm.region" placeholder="cn-beijing" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">Bucket <span class="text-danger">*</span></label>
            <input v-model="tosForm.bucket" placeholder="bucket-name" class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">Access Key <span class="text-danger">*</span></label>
            <input v-model="tosForm.access_key" type="password" placeholder="AK..." class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">Secret Key <span class="text-danger">*</span></label>
            <input v-model="tosForm.secret_key" type="password" placeholder="SK..." class="h-9 px-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
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

const apiForm = ref({
  name: '',
  platform: 'volcengine_ark',
  api_key: '',
  base_url: 'https://ark.cn-beijing.volces.com/api/v3',
  total_concurrency: 5,
  is_active: true,
})

const tosForm = ref({
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

async function fetchTosConfig() {
  try {
    const res = await api.get('/admin/system-config/tos')
    const data = res.data.config_value || {}
    tosForm.value = {
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

async function saveTos() {
  if (!tosForm.value.bucket || !tosForm.value.access_key || !tosForm.value.secret_key) {
    alert('请填写 Bucket、Access Key 和 Secret Key')
    return
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
  fetchTosConfig()
})
</script>
