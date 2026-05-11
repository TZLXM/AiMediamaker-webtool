<template>
  <div class="page-container">
    <div class="page-header">
      <h1>{{ isEdit ? '编辑模型' : '新增模型' }}</h1>
    </div>
    <div class="form-card">
      <div class="form-grid">
        <div class="form-field">
          <label>显示名称</label>
          <input v-model="form.name" placeholder="如：Seedance 2.0" />
        </div>
        <div class="form-field">
          <label>模型ID</label>
          <input v-model="form.model_id" placeholder="如：doubao-seedance-2-0-260128" />
        </div>
        <div class="form-field">
          <label>生成模式</label>
          <select v-model="form.mode">
            <option value="image">图片</option>
            <option value="video">视频</option>
          </select>
        </div>
        <div class="form-field">
          <label>并发限制</label>
          <input v-model.number="form.concurrency_limit" type="number" min="1" />
        </div>
        <div class="form-field full">
          <label>描述</label>
          <textarea v-model="form.description" rows="2" placeholder="模型功能描述..."></textarea>
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
        <button class="btn-primary" @click="save">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
// import api from '@/api'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => route.name === 'model-edit')
// const modelId = computed(() => route.params.id)

const form = ref({
  name: '',
  model_id: '',
  mode: 'image' as 'image' | 'video',
  concurrency_limit: 2,
  description: '',
  is_active: true,
})

async function fetchModel() {
  if (!isEdit.value) return
  // TODO: 接入获取单个模型API
}

async function save() {
  // TODO: 接入保存API
  router.push('/models')
}

onMounted(fetchModel)
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
</style>
