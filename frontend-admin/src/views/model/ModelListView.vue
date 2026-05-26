<template>
  <div class="max-w-[1200px]">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-xl font-semibold">模型管理</h1>
      <button class="flex items-center gap-1.5 px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer transition-colors duration-200 hover:bg-accent-hover" @click="$router.push('/models/create')">
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
              <span class="px-2 py-0.5 rounded text-xs font-medium" :class="model.mode === 'image' ? 'bg-accent/15 text-accent' : 'bg-warning/15 text-warning'">{{ model.mode === 'image' ? '图片' : '视频' }}</span>
            </td>
            <td class="px-4 py-3 border-t border-borderc">{{ model.concurrency_limit }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <span class="px-2 py-0.5 rounded text-xs" :class="model.is_active ? 'bg-success/15 text-success' : 'bg-txtm/15 text-txtm'">
                {{ model.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td class="px-4 py-3 border-t border-borderc">
              <button class="px-2 py-1 bg-transparent border-none text-accent text-[13px] cursor-pointer" @click="editModel(model.id)">编辑</button>
              <button class="px-2 py-1 bg-transparent border-none text-danger text-[13px] cursor-pointer" @click="deleteModel(model.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="models.length === 0" class="text-center py-10 text-txtm text-sm">暂无模型配置</div>
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
  try {
    const res = await api.get('/admin/model-configs')
    models.value = res.data
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取模型列表失败')
  }
}

function editModel(id: number) {
  router.push(`/models/edit/${id}`)
}

async function deleteModel(id: number) {
  if (!confirm('确定要删除该模型配置吗？')) return
  try {
    await api.delete(`/admin/model-configs/${id}`)
    await fetchModels()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

onMounted(fetchModels)
</script>
