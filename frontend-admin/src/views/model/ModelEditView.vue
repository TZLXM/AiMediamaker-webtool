<template>
  <div class="page-container">
    <div class="page-header">
      <h1>{{ isEdit ? '编辑模型' : '新增模型' }}</h1>
    </div>
    <div class="form-card">
      <div class="form-grid">
        <div class="form-field">
          <label>显示名称 <span class="required">*</span></label>
          <input v-model="form.name" placeholder="如：Seedance 2.0" />
        </div>
        <div class="form-field">
          <label>模型ID <span class="required">*</span></label>
          <input v-model="form.model_id" placeholder="如：doubao-seedance-2-0-260128" />
        </div>
        <div class="form-field">
          <label>关联 API 配置 <span class="required">*</span></label>
          <select v-model.number="form.api_config_id">
            <option value="0" disabled>请选择 API 配置</option>
            <option v-for="api in apiConfigs" :key="api.id" :value="api.id">
              {{ api.name }}
            </option>
          </select>
        </div>
        <div class="form-field">
          <label>生成模式 <span class="required">*</span></label>
          <select v-model="form.mode">
            <option value="image">图片</option>
            <option value="video">视频</option>
          </select>
        </div>
        <div class="form-field">
          <label>并发限制</label>
          <input v-model.number="form.concurrency_limit" type="number" min="1" />
        </div>
        <div class="form-field">
          <label>排序权重</label>
          <input v-model.number="form.sort_order" type="number" />
        </div>
        <div class="form-field full">
          <label>描述</label>
          <textarea v-model="form.description" rows="2" placeholder="模型功能描述..."></textarea>
        </div>
        <div class="form-field full">
          <label>支持的输入类型（逗号分隔）</label>
          <input v-model="inputTypesStr" placeholder="如：image,video,audio" />
        </div>
        <div class="form-field full">
          <label class="checkbox">
            <input v-model="form.is_active" type="checkbox" />
            启用该模型
          </label>
        </div>
      </div>
      <div class="form-actions">
        <button class="btn-secondary" @click="$router.back()">取消</button>
        <button class="btn-primary" @click="save" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import type { ModelConfig, ApiConfig } from '@/types'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => route.name === 'model-edit')
const modelId = computed(() => route.params.id as string)

const apiConfigs = ref<ApiConfig[]>([])
const saving = ref(false)

const form = ref({
  name: '',
  model_id: '',
  api_config_id: 0,
  mode: 'image' as 'image' | 'video',
  concurrency_limit: 2,
  sort_order: 0,
  description: '',
  parameters_schema: [] as any[],
  supported_input_types: [] as string[],
  is_active: true,
})

const inputTypesStr = computed({
  get: () => form.value.supported_input_types.join(','),
  set: (val: string) => {
    form.value.supported_input_types = val.split(',').map(s => s.trim()).filter(Boolean)
  },
})

async function fetchApiConfigs() {
  try {
    const res = await api.get('/admin/api-configs')
    apiConfigs.value = res.data
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取 API 配置失败')
  }
}

async function fetchModel() {
  if (!isEdit.value) return
  try {
    const res = await api.get(`/admin/model-configs/${modelId.value}`)
    const data: ModelConfig = res.data
    form.value = {
      name: data.name,
      model_id: data.model_id,
      api_config_id: data.api_config_id,
      mode: data.mode,
      concurrency_limit: data.concurrency_limit,
      sort_order: data.sort_order,
      description: data.description || '',
      parameters_schema: data.parameters_schema || [],
      supported_input_types: data.supported_input_types || [],
      is_active: data.is_active,
    }
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取模型信息失败')
    router.back()
  }
}

async function save() {
  if (!form.value.name || !form.value.model_id || !form.value.api_config_id) {
    alert('请填写名称、模型ID并选择关联的 API 配置')
    return
  }
  saving.value = true
  try {
    const payload = {
      ...form.value,
      parameters_schema: form.value.parameters_schema || [],
      supported_input_types: form.value.supported_input_types || [],
    }
    if (isEdit.value) {
      await api.put(`/admin/model-configs/${modelId.value}`, payload)
    } else {
      await api.post('/admin/model-configs', payload)
    }
    router.push('/models')
  } catch (e: any) {
    alert(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await fetchApiConfigs()
  await fetchModel()
})
</script>

<style scoped>
.page-container {
  max-width: 800px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 20px;
  font-weight: 600;
}

.form-card {
  background: var(--color-card);
  border: 1px solid var(--color-borderc);
  border-radius: 12px;
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field.full {
  grid-column: 1 / -1;
}

.form-field label {
  font-size: 13px;
  color: var(--color-txts);
}

.form-field .required {
  color: var(--color-danger);
}

.form-field input,
.form-field select,
.form-field textarea {
  padding: 10px 12px;
  background: var(--color-active);
  border: 1px solid var(--color-borderc);
  border-radius: 8px;
  color: var(--color-txtp);
  font-size: 14px;
  outline: none;
}

.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  border-color: var(--color-accent);
}

.form-field .checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-txtp);
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--color-borderc);
}

.btn-secondary {
  padding: 8px 16px;
  background: var(--color-active);
  border: 1px solid var(--color-borderc);
  border-radius: 8px;
  color: var(--color-txts);
  font-size: 13px;
  cursor: pointer;
}

.btn-primary {
  padding: 8px 16px;
  background: var(--color-accent);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--color-accent-hover);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
