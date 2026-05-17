<template>
  <div class="page-container">
    <div class="page-header">
      <h1>系统配置</h1>
    </div>
    <div class="config-sections">
      <!-- API配置 -->
      <div class="config-card">
        <div class="card-header">
          <h2>API 配置</h2>
          <button class="btn-primary" @click="openApiForm()">新增配置</button>
        </div>

        <!-- 新增/编辑表单 -->
        <div v-if="showApiForm" class="form-card">
          <h3>{{ editingApiId ? '编辑 API 配置' : '新增 API 配置' }}</h3>
          <div class="form-grid">
            <div class="form-field">
              <label>配置名称 <span class="required">*</span></label>
              <input v-model="apiForm.name" placeholder="如：火山方舟主账号" />
            </div>
            <div class="form-field">
              <label>平台类型 <span class="required">*</span></label>
              <select v-model="apiForm.platform">
                <option value="volcengine_ark">火山方舟</option>
              </select>
            </div>
            <div class="form-field full">
              <label>API Key <span class="required">*</span></label>
              <input v-model="apiForm.api_key" type="password" placeholder="sk-xxx..." />
            </div>
            <div class="form-field full">
              <label>Base URL</label>
              <input v-model="apiForm.base_url" placeholder="https://ark.cn-beijing.volces.com/api/v3" />
            </div>
            <div class="form-field">
              <label>总并发限制</label>
              <input v-model.number="apiForm.total_concurrency" type="number" min="1" />
            </div>
            <div class="form-field">
              <label class="checkbox">
                <input v-model="apiForm.is_active" type="checkbox" />
                启用该配置
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn-secondary" @click="closeApiForm">取消</button>
            <button class="btn-primary" @click="saveApi" :disabled="savingApi">
              {{ savingApi ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>

        <div class="config-list">
          <div v-for="api in apiConfigs" :key="api.id" class="config-item">
            <div class="config-info">
              <span class="config-name">{{ api.name }}</span>
              <span class="config-detail">{{ api.base_url }}</span>
            </div>
            <div class="config-meta">
              <span class="tag" :class="api.is_active ? 'active' : 'inactive'">
                {{ api.is_active ? '启用' : '禁用' }}
              </span>
              <span class="concurrency">并发: {{ api.total_concurrency }}</span>
            </div>
            <div class="config-actions">
              <button class="btn-text" @click="openApiForm(api)">编辑</button>
              <button class="btn-text danger" @click="deleteApi(api.id)">删除</button>
            </div>
          </div>
          <div v-if="apiConfigs.length === 0" class="empty-tip">暂无 API 配置</div>
        </div>
      </div>

      <!-- TOS配置 -->
      <div class="config-card">
        <div class="card-header">
          <h2>TOS 对象存储配置</h2>
          <button class="btn-primary" @click="saveTos" :disabled="savingTos">
            {{ savingTos ? '保存中...' : '保存配置' }}
          </button>
        </div>
        <p class="form-tip">修改后将覆盖服务器环境变量中的 TOS 配置。</p>
        <div class="form-grid">
          <div class="form-field">
            <label>Endpoint</label>
            <input v-model="tosForm.endpoint" placeholder="tos-cn-beijing.volces.com" />
          </div>
          <div class="form-field">
            <label>Region</label>
            <input v-model="tosForm.region" placeholder="cn-beijing" />
          </div>
          <div class="form-field">
            <label>Bucket <span class="required">*</span></label>
            <input v-model="tosForm.bucket" placeholder="bucket-name" />
          </div>
          <div class="form-field">
            <label>Access Key <span class="required">*</span></label>
            <input v-model="tosForm.access_key" type="password" placeholder="AK..." />
          </div>
          <div class="form-field">
            <label>Secret Key <span class="required">*</span></label>
            <input v-model="tosForm.secret_key" type="password" placeholder="SK..." />
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

<style scoped>
.page-container { max-width: 900px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 20px; font-weight: 600; }

.config-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-card {
  background: var(--color-card);
  border: 1px solid var(--color-borderc);
  border-radius: 12px;
  padding: 24px;
}

.config-card h2 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.config-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--color-active);
  border-radius: 8px;
}

.config-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}
.config-name { font-size: 14px; font-weight: 500; }
.config-detail { font-size: 12px; color: var(--color-txtm); }

.config-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 16px;
}
.tag {
  padding: 2px 8px; border-radius: 4px; font-size: 12px;
}
.tag.active { background: rgba(34, 197, 94, 0.15); color: var(--color-success); }
.tag.inactive { background: rgba(113, 113, 122, 0.15); color: var(--color-txtm); }
.concurrency { font-size: 12px; color: var(--color-txts); }

.config-actions {
  display: flex; gap: 8px;
}
.btn-text {
  padding: 4px 8px; background: transparent; border: none;
  color: var(--color-accent); font-size: 13px; cursor: pointer;
}
.btn-text.danger { color: var(--color-danger); }

.btn-primary {
  padding: 8px 16px; background: var(--color-accent);
  border: none; border-radius: 8px; color: white;
  font-size: 13px; cursor: pointer;
}
.btn-primary:hover { background: var(--color-accent-hover); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-secondary {
  padding: 8px 16px; background: var(--color-active);
  border: 1px solid var(--color-borderc); border-radius: 8px;
  color: var(--color-txts); font-size: 13px; cursor: pointer;
}

.form-card {
  background: var(--color-active);
  border: 1px solid var(--color-borderc);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 16px;
}
.form-card h3 {
  font-size: 14px; font-weight: 600;
  margin-bottom: 16px; color: var(--color-txtp);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}
.form-field {
  display: flex; flex-direction: column; gap: 6px;
}
.form-field.full { grid-column: 1 / -1; }
.form-field label { font-size: 13px; color: var(--color-txts); }
.form-field .required { color: var(--color-danger); }
.form-field input,
.form-field select {
  padding: 10px 12px; background: var(--color-card);
  border: 1px solid var(--color-borderc); border-radius: 8px;
  color: var(--color-txtp); font-size: 14px; outline: none;
}
.form-field input:focus,
.form-field select:focus { border-color: var(--color-accent); }
.form-field input:disabled {
  opacity: 0.5; cursor: not-allowed;
}

.form-field .checkbox {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; color: var(--color-txtp); cursor: pointer;
}

.form-actions {
  display: flex; justify-content: flex-end; gap: 12px;
}

.empty-tip {
  text-align: center; padding: 24px;
  color: var(--color-txtm); font-size: 14px;
}
.form-tip {
  font-size: 12px; color: var(--color-txtm);
  margin-bottom: 12px;
}
</style>
