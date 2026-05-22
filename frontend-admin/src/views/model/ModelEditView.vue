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

      <!-- 参数配置 -->
      <div class="params-section">
        <div class="params-header">
          <h3>参数配置</h3>
          <button class="btn-small" @click="addParam">
            + 添加参数
          </button>
        </div>
        <div v-if="form.parameters_schema.length === 0" class="params-empty">
          暂无参数，点击上方按钮添加
        </div>
        <div v-for="(param, idx) in form.parameters_schema" :key="idx" class="param-card">
          <div class="param-card-header">
            <div class="param-info">
              <span class="param-key">{{ param.key }}</span>
              <span class="param-label">{{ param.label }}</span>
              <span class="param-type">{{ param.type }}</span>
            </div>
            <div class="param-actions">
              <button class="btn-icon" @click="toggleParamEdit(idx)">
                {{ editingParamIndex === idx ? '收起' : '编辑' }}
              </button>
              <button class="btn-icon danger" @click="removeParam(idx)">
                删除
              </button>
            </div>
          </div>
          <div v-if="editingParamIndex === idx" class="param-form">
            <div class="form-grid">
              <div class="form-field">
                <label>参数 key <span class="required">*</span></label>
                <input v-model="param.key" placeholder="如：ratio、resolution、size" />
              </div>
              <div class="form-field">
                <label>显示名称 <span class="required">*</span></label>
                <input v-model="param.label" placeholder="如：选择比例、分辨率" />
              </div>
              <div class="form-field">
                <label>类型 <span class="required">*</span></label>
                <select v-model="param.type">
                  <option value="select">下拉选择 (select)</option>
                  <option value="number">数字 (number)</option>
                  <option value="boolean">开关 (boolean)</option>
                  <option value="text">文本 (text)</option>
                </select>
              </div>
              <div class="form-field">
                <label>是否必填</label>
                <select v-model="param.required">
                  <option :value="true">是</option>
                  <option :value="false">否</option>
                </select>
              </div>
              <div class="form-field">
                <label>默认值</label>
                <input v-if="param.type === 'text'" v-model="param.default" placeholder="默认值" />
                <input v-else-if="param.type === 'number'" v-model.number="param.default" type="number" placeholder="默认值" />
                <select v-else-if="param.type === 'boolean'" v-model="param.default">
                  <option :value="true">是</option>
                  <option :value="false">否</option>
                  <option :value="undefined">不设置</option>
                </select>
                <input v-else v-model="param.default" placeholder="默认值" />
              </div>
              <div v-if="param.type === 'number'" class="form-field">
                <label>最小值</label>
                <input v-model.number="param.min" type="number" placeholder="min" />
              </div>
              <div v-if="param.type === 'number'" class="form-field">
                <label>最大值</label>
                <input v-model.number="param.max" type="number" placeholder="max" />
              </div>
              <div class="form-field full">
                <label>描述</label>
                <input v-model="param.description" placeholder="参数说明..." />
              </div>
            </div>
            <!-- 选项配置（仅 select 类型） -->
            <div v-if="param.type === 'select'" class="options-section">
              <div class="options-header">
                <label>选项列表</label>
                <button class="btn-small" @click="addOption(param)">+ 添加选项</button>
              </div>
              <div v-for="(opt, oidx) in param.options" :key="oidx" class="option-row">
                <input v-model="opt.value" placeholder="值" class="opt-input" />
                <input v-model="opt.label" placeholder="显示标签" class="opt-input" />
                <input v-model="opt.name" placeholder="名称（可选）" class="opt-input" />
                <button class="btn-icon danger" @click="removeOption(param, oidx)">删除</button>
              </div>
              <div v-if="!param.options || param.options.length === 0" class="params-empty">
                暂无选项，点击上方按钮添加
              </div>
            </div>
          </div>
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

const editingParamIndex = ref<number | null>(null)

function addParam() {
  form.value.parameters_schema.push({
    key: '',
    label: '',
    type: 'select',
    required: false,
    default: undefined,
    options: [],
    min: undefined,
    max: undefined,
    description: '',
  })
  editingParamIndex.value = form.value.parameters_schema.length - 1
}

function removeParam(idx: number) {
  form.value.parameters_schema.splice(idx, 1)
  if (editingParamIndex.value === idx) {
    editingParamIndex.value = null
  }
}

function toggleParamEdit(idx: number) {
  editingParamIndex.value = editingParamIndex.value === idx ? null : idx
}

function addOption(param: any) {
  if (!param.options) param.options = []
  param.options.push({ value: '', label: '', name: '' })
}

function removeOption(param: any, oidx: number) {
  param.options.splice(oidx, 1)
}

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

.params-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--color-borderc);
}

.params-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.params-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-txtp);
}

.params-empty {
  color: var(--color-txtm);
  font-size: 13px;
  padding: 16px;
  text-align: center;
  background: var(--color-active);
  border-radius: 8px;
}

.param-card {
  background: var(--color-active);
  border: 1px solid var(--color-borderc);
  border-radius: 10px;
  margin-bottom: 10px;
  overflow: hidden;
}

.param-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
}

.param-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.param-key {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-accent);
  background: #4f8ff71a;
  padding: 2px 8px;
  border-radius: 4px;
}

.param-label {
  font-size: 14px;
  color: var(--color-txtp);
}

.param-type {
  font-size: 11px;
  color: var(--color-txts);
  background: var(--color-hover);
  padding: 2px 8px;
  border-radius: 4px;
}

.param-actions {
  display: flex;
  gap: 8px;
}

.btn-small {
  padding: 6px 12px;
  background: var(--color-accent);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 12px;
  cursor: pointer;
}

.btn-small:hover {
  background: var(--color-accent-hover);
}

.btn-icon {
  padding: 4px 10px;
  background: var(--color-hover);
  border: 1px solid var(--color-borderc);
  border-radius: 6px;
  color: var(--color-txts);
  font-size: 12px;
  cursor: pointer;
}

.btn-icon:hover {
  color: var(--color-txtp);
  background: var(--color-active);
}

.btn-icon.danger {
  color: var(--color-danger);
}

.btn-icon.danger:hover {
  background: #ff453a1a;
}

.param-form {
  padding: 16px;
  border-top: 1px solid var(--color-borderc);
  background: var(--color-card);
}

.options-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-borderc);
}

.options-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.options-header label {
  font-size: 13px;
  color: var(--color-txts);
}

.option-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.opt-input {
  flex: 1;
  padding: 8px 10px;
  background: var(--color-active);
  border: 1px solid var(--color-borderc);
  border-radius: 6px;
  color: var(--color-txtp);
  font-size: 13px;
  outline: none;
}

.opt-input:focus {
  border-color: var(--color-accent);
}
</style>
