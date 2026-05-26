<template>
  <div class="max-w-[1200px]">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-xl font-semibold">模型管理</h1>
      <button
        class="flex items-center gap-1.5 px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer transition-colors duration-200 hover:bg-accent-hover"
        @click="openModal()"
      >
        <PlusIcon :size="16" />
        新增模型
      </button>
    </div>
    <div class="bg-card border border-borderc rounded-card overflow-hidden">
      <table class="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">名称</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">模型ID</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">模式</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">并发限制</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">状态</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="model in models" :key="model.id">
            <td class="px-4 py-3 border-t border-borderc">{{ model.name }}</td>
            <td class="px-4 py-3 border-t border-borderc font-mono text-xs text-txts">{{ model.model_id }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <span
                class="px-2 py-0.5 rounded text-xs font-medium"
                :class="model.mode === 'image' ? 'bg-accent/15 text-accent' : 'bg-warning/15 text-warning'"
              >
                {{ model.mode === 'image' ? '图片' : '视频' }}
              </span>
            </td>
            <td class="px-4 py-3 border-t border-borderc">{{ model.concurrency_limit }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <span
                class="px-2 py-0.5 rounded text-xs"
                :class="model.is_active ? 'bg-success/15 text-success' : 'bg-txtm/15 text-txtm'"
              >
                {{ model.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td class="px-4 py-3 border-t border-borderc">
              <button class="px-2 py-1 bg-transparent border-none text-accent text-[13px] cursor-pointer" @click="openModal(model)">
                编辑
              </button>
              <button class="px-2 py-1 bg-transparent border-none text-danger text-[13px] cursor-pointer" @click="confirmDelete(model)">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="models.length === 0" class="text-center py-10 text-txtm text-sm">暂无模型配置</div>
    </div>

    <!-- 新增/编辑模型弹窗 -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-[1000]"
      @click.self="closeModal"
    >
      <div class="bg-card border border-borderc rounded-card p-6 w-[560px] max-h-[90vh] overflow-y-auto">
        <h2 class="text-xl font-semibold mb-6">{{ isEdit ? '编辑模型' : '新增模型' }}</h2>

        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">显示名称 <span class="text-danger">*</span></label>
            <input
              v-model="form.name"
              placeholder="如：Seedance 2.0"
              class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
            />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">模型ID <span class="text-danger">*</span></label>
            <input
              v-model="form.model_id"
              placeholder="如：doubao-seedance-2-0-260128"
              class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
            />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">关联 API 配置 <span class="text-danger">*</span></label>
            <select
              v-model.number="form.api_config_id"
              class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
            >
              <option value="0" disabled>请选择 API 配置</option>
              <option v-for="api in apiConfigs" :key="api.id" :value="api.id">{{ api.name }}</option>
            </select>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">生成模式 <span class="text-danger">*</span></label>
            <select
              v-model="form.mode"
              class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
            >
              <option value="image">图片</option>
              <option value="video">视频</option>
            </select>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">并发限制</label>
            <input
              v-model.number="form.concurrency_limit"
              type="number"
              min="1"
              class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
            />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] text-txts">排序权重</label>
            <input
              v-model.number="form.sort_order"
              type="number"
              class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
            />
          </div>
          <div class="flex flex-col gap-1.5 col-span-2">
            <label class="text-[13px] text-txts">描述</label>
            <textarea
              v-model="form.description"
              rows="2"
              placeholder="模型功能描述..."
              class="px-3 py-2 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
            ></textarea>
          </div>
          <div class="flex flex-col gap-1.5 col-span-2">
            <label class="text-[13px] text-txts">支持文件类型</label>
            <div class="flex gap-4">
              <label class="flex items-center gap-2 text-sm text-txtp cursor-pointer">
                <input v-model="supportedInputTypes" type="checkbox" value="image" />
                图片
              </label>
              <label class="flex items-center gap-2 text-sm text-txtp cursor-pointer">
                <input v-model="supportedInputTypes" type="checkbox" value="video" />
                视频
              </label>
              <label class="flex items-center gap-2 text-sm text-txtp cursor-pointer">
                <input v-model="supportedInputTypes" type="checkbox" value="audio" />
                音频
              </label>
            </div>
          </div>
          <div class="flex flex-col gap-1.5 col-span-2">
            <label class="flex items-center gap-2 text-sm text-txtp cursor-pointer">
              <input v-model="form.is_active" type="checkbox" />
              启用该模型
            </label>
          </div>
        </div>

        <!-- 参数配置 -->
        <div class="mt-6 pt-6 border-t border-borderc">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-[15px] font-semibold text-txtp">参数配置</h3>
            <button
              class="px-3 h-7 bg-accent border-none rounded-btn text-white text-xs cursor-pointer hover:bg-accent-hover"
              @click="addParam"
            >
              + 添加参数
            </button>
          </div>
          <div v-if="form.parameters_schema.length === 0" class="text-txtm text-[13px] p-4 text-center bg-active rounded-btn">
            暂无参数，点击上方按钮添加
          </div>
          <div
            v-for="(param, idx) in form.parameters_schema"
            :key="idx"
            class="bg-active border border-borderc rounded-card mb-2.5 overflow-hidden"
          >
            <div class="flex justify-between items-center px-4 py-3">
              <div class="flex items-center gap-2.5">
                <span class="font-mono text-xs text-accent bg-accent/15 px-2 py-0.5 rounded">{{ param.key }}</span>
                <span class="text-sm text-txtp">{{ param.label }}</span>
                <span class="text-[11px] text-txts bg-hover px-2 py-0.5 rounded">{{ param.type }}</span>
              </div>
              <div class="flex gap-2">
                <button
                  class="px-2.5 py-1 bg-hover border border-borderc rounded-btn text-txts text-xs cursor-pointer hover:text-txtp hover:bg-active"
                  @click="toggleParamEdit(idx)"
                >
                  {{ editingParamIndex === idx ? '收起' : '编辑' }}
                </button>
                <button
                  class="px-2.5 py-1 bg-hover border border-borderc rounded-btn text-danger text-xs cursor-pointer hover:bg-danger/10"
                  @click="removeParam(idx)"
                >
                  删除
                </button>
              </div>
            </div>
            <div v-if="editingParamIndex === idx" class="p-4 border-t border-borderc bg-card">
              <div class="grid grid-cols-2 gap-4">
                <div class="flex flex-col gap-1.5">
                  <label class="text-[13px] text-txts">参数 key <span class="text-danger">*</span></label>
                  <input
                    v-model="param.key"
                    placeholder="如：ratio、resolution、size"
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  />
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="text-[13px] text-txts">显示名称 <span class="text-danger">*</span></label>
                  <input
                    v-model="param.label"
                    placeholder="如：选择比例、分辨率"
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  />
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="text-[13px] text-txts">类型 <span class="text-danger">*</span></label>
                  <select
                    v-model="param.type"
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  >
                    <option value="select">下拉选择 (select)</option>
                    <option value="number">数字 (number)</option>
                    <option value="boolean">开关 (boolean)</option>
                    <option value="text">文本 (text)</option>
                  </select>
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="text-[13px] text-txts">是否必填</label>
                  <select
                    v-model="param.required"
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  >
                    <option :value="true">是</option>
                    <option :value="false">否</option>
                  </select>
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="text-[13px] text-txts">默认值</label>
                  <input
                    v-if="param.type === 'text'"
                    v-model="param.default"
                    placeholder="默认值"
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  />
                  <input
                    v-else-if="param.type === 'number'"
                    v-model.number="param.default"
                    type="number"
                    placeholder="默认值"
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  />
                  <select
                    v-else-if="param.type === 'boolean'"
                    v-model="param.default"
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  >
                    <option :value="true">是</option>
                    <option :value="false">否</option>
                    <option :value="undefined">不设置</option>
                  </select>
                  <input
                    v-else
                    v-model="param.default"
                    placeholder="默认值"
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  />
                </div>
                <div v-if="param.type === 'number'" class="flex flex-col gap-1.5">
                  <label class="text-[13px] text-txts">最小值</label>
                  <input
                    v-model.number="param.min"
                    type="number"
                    placeholder="min"
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  />
                </div>
                <div v-if="param.type === 'number'" class="flex flex-col gap-1.5">
                  <label class="text-[13px] text-txts">最大值</label>
                  <input
                    v-model.number="param.max"
                    type="number"
                    placeholder="max"
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  />
                </div>
                <div class="flex flex-col gap-1.5 col-span-2">
                  <label class="text-[13px] text-txts">描述</label>
                  <input
                    v-model="param.description"
                    placeholder="参数说明..."
                    class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent"
                  />
                </div>
              </div>
              <!-- 选项配置（仅 select 类型） -->
              <div v-if="param.type === 'select'" class="mt-4 pt-4 border-t border-borderc">
                <div class="flex justify-between items-center mb-3">
                  <label class="text-[13px] text-txts">选项列表</label>
                  <button
                    class="px-3 h-7 bg-accent border-none rounded-btn text-white text-xs cursor-pointer hover:bg-accent-hover"
                    @click="addOption(param)"
                  >
                    + 添加选项
                  </button>
                </div>
                <div v-for="(opt, oidx) in param.options" :key="oidx" class="flex gap-2 items-center mb-2">
                  <input
                    v-model="opt.value"
                    placeholder="值"
                    class="flex-1 h-8 px-2.5 bg-active border border-borderc rounded-btn text-txtp text-[13px] outline-none focus:border-accent"
                  />
                  <input
                    v-model="opt.label"
                    placeholder="显示标签"
                    class="flex-1 h-8 px-2.5 bg-active border border-borderc rounded-btn text-txtp text-[13px] outline-none focus:border-accent"
                  />
                  <input
                    v-model="opt.name"
                    placeholder="名称（可选）"
                    class="flex-1 h-8 px-2.5 bg-active border border-borderc rounded-btn text-txtp text-[13px] outline-none focus:border-accent"
                  />
                  <button
                    class="px-2.5 py-1 bg-hover border border-borderc rounded-btn text-danger text-xs cursor-pointer hover:bg-danger/10"
                    @click="removeOption(param, oidx)"
                  >
                    删除
                  </button>
                </div>
                <div
                  v-if="!param.options || param.options.length === 0"
                  class="text-txtm text-[13px] p-4 text-center bg-active rounded-btn"
                >
                  暂无选项，点击上方按钮添加
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6 pt-6 border-t border-borderc">
          <button
            class="px-4 h-9 bg-active border border-borderc rounded-btn text-txts text-[13px] cursor-pointer"
            @click="closeModal"
          >
            取消
          </button>
          <button
            class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed"
            :disabled="saving"
            @click="save"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from 'lucide-vue-next'
import api from '@/api'
import type { ModelConfig, ApiConfig } from '@/types'

const PlusIcon = Plus

const models = ref<ModelConfig[]>([])
const apiConfigs = ref<ApiConfig[]>([])
const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
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

const supportedInputTypes = ref<string[]>([])
const editingParamIndex = ref<number | null>(null)

function resetForm() {
  form.value = {
    name: '',
    model_id: '',
    api_config_id: 0,
    mode: 'image',
    concurrency_limit: 2,
    sort_order: 0,
    description: '',
    parameters_schema: [],
    supported_input_types: [],
    is_active: true,
  }
  supportedInputTypes.value = []
  editingParamIndex.value = null
  isEdit.value = false
  editingId.value = null
}

function openModal(model?: ModelConfig) {
  resetForm()
  if (model) {
    isEdit.value = true
    editingId.value = model.id
    form.value = {
      name: model.name,
      model_id: model.model_id,
      api_config_id: model.api_config_id,
      mode: model.mode,
      concurrency_limit: model.concurrency_limit,
      sort_order: model.sort_order,
      description: model.description || '',
      parameters_schema: model.parameters_schema || [],
      supported_input_types: model.supported_input_types || [],
      is_active: model.is_active,
    }
    supportedInputTypes.value = model.supported_input_types || []
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  resetForm()
}

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

async function fetchModels() {
  try {
    const res = await api.get('/admin/model-configs')
    models.value = res.data
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取模型列表失败')
  }
}

async function fetchApiConfigs() {
  try {
    const res = await api.get('/admin/api-configs')
    apiConfigs.value = res.data
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取 API 配置失败')
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
      supported_input_types: supportedInputTypes.value,
      parameters_schema: form.value.parameters_schema || [],
    }
    if (isEdit.value && editingId.value) {
      await api.put(`/admin/model-configs/${editingId.value}`, payload)
    } else {
      await api.post('/admin/model-configs', payload)
    }
    closeModal()
    await fetchModels()
  } catch (e: any) {
    alert(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

function confirmDelete(model: ModelConfig) {
  if (!confirm('删除后该模型的配置将无法恢复，是否继续？')) return
  deleteModel(model.id)
}

async function deleteModel(id: number) {
  try {
    await api.delete(`/admin/model-configs/${id}`)
    await fetchModels()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

onMounted(async () => {
  await fetchModels()
  await fetchApiConfigs()
})
</script>
