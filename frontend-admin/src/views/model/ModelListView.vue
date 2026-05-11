<template>
  <div class="page-container">
    <div class="page-header">
      <h1>模型管理</h1>
      <button class="btn-primary" @click="$router.push('/models/create')">
        <PlusIcon :size="16" />
        新增模型
      </button>
    </div>
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>名称</th>
            <th>模型ID</th>
            <th>模式</th>
            <th>并发限制</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="model in models" :key="model.id">
            <td>{{ model.name }}</td>
            <td class="mono">{{ model.model_id }}</td>
            <td>
              <span class="tag" :class="model.mode">{{ model.mode === 'image' ? '图片' : '视频' }}</span>
            </td>
            <td>{{ model.concurrency_limit }}</td>
            <td>
              <span class="status-dot" :class="model.is_active ? 'active' : 'inactive'">
                {{ model.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td>
              <button class="btn-text" @click="editModel(model.id)">编辑</button>
              <button class="btn-text danger" @click="deleteModel(model.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from 'lucide-vue-next'
import api from '@/api'
import type { ModelConfig } from '@/types'

const PlusIcon = Plus
const router = useRouter()

const models = ref<ModelConfig[]>([])

async function fetchModels() {
  const res = await api.get('/models/list')
  models.value = res.data
}

function editModel(id: number) {
  router.push(`/models/edit/${id}`)
}

async function deleteModel(_id: number) {
  if (!confirm('确定要删除该模型配置吗？')) return
  // TODO: 接入删除API
}

onMounted(fetchModels)
</script>

<style scoped>
.page-container {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 20px;
  font-weight: 600;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--color-accent);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: var(--color-accent-hover);
}

.table-container {
  background: var(--color-card);
  border: 1px solid var(--color-borderc);
  border-radius: 12px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  background: var(--color-active);
  color: var(--color-txts);
  font-weight: 500;
  font-size: 13px;
}

.data-table td {
  padding: 12px 16px;
  border-top: 1px solid var(--color-borderc);
}

.mono {
  font-family: monospace;
  font-size: 12px;
  color: var(--color-txts);
}

.tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.tag.image {
  background: rgba(99, 102, 241, 0.15);
  color: var(--color-accent);
}

.tag.video {
  background: rgba(245, 158, 11, 0.15);
  color: var(--color-warning);
}

.status-dot {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-dot.active {
  background: rgba(34, 197, 94, 0.15);
  color: var(--color-success);
}

.status-dot.inactive {
  background: rgba(113, 113, 122, 0.15);
  color: var(--color-txtm);
}

.btn-text {
  padding: 4px 8px;
  background: transparent;
  border: none;
  color: var(--color-accent);
  font-size: 13px;
  cursor: pointer;
}

.btn-text.danger {
  color: var(--color-danger);
}
</style>
