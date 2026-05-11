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
          <button class="btn-primary" @click="showApiModal = true">新增配置</button>
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
              <button class="btn-text" @click="editApi(api)">编辑</button>
              <button class="btn-text danger" @click="deleteApi(api.id)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- TOS配置 -->
      <div class="config-card">
        <h2>TOS 对象存储配置</h2>
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
            <label>Bucket</label>
            <input v-model="tosForm.bucket" />
          </div>
          <div class="form-field">
            <label>Access Key</label>
            <input v-model="tosForm.access_key" type="password" />
          </div>
          <div class="form-field">
            <label>Secret Key</label>
            <input v-model="tosForm.secret_key" type="password" />
          </div>
        </div>
        <div class="form-actions">
          <button class="btn-primary" @click="saveTos">保存 TOS 配置</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
// import api from '@/api'
import type { ApiConfig } from '@/types'

const apiConfigs = ref<ApiConfig[]>([])
const showApiModal = ref(false)

const tosForm = ref({
  endpoint: '',
  region: '',
  bucket: '',
  access_key: '',
  secret_key: '',
})

async function fetchConfigs() {
  // TODO: 接入API配置列表
}

function editApi(_config: ApiConfig) {
  // TODO
}

async function deleteApi(_id: number) {
  if (!confirm('确定删除该API配置？')) return
  // TODO
}

async function saveTos() {
  // TODO: 接入保存TOS配置API
}

onMounted(fetchConfigs)
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
  background: var(--bg-secondary);
  border: 1px solid var(--border);
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
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.config-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.config-name { font-size: 14px; font-weight: 500; }
.config-detail { font-size: 12px; color: var(--text-muted); }

.config-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}
.tag {
  padding: 2px 8px; border-radius: 4px; font-size: 12px;
}
.tag.active { background: rgba(34, 197, 94, 0.15); color: var(--accent-success); }
.tag.inactive { background: rgba(113, 113, 122, 0.15); color: var(--text-muted); }
.concurrency { font-size: 12px; color: var(--text-secondary); }

.config-actions {
  display: flex; gap: 8px;
}
.btn-text {
  padding: 4px 8px; background: transparent; border: none;
  color: var(--accent); font-size: 13px; cursor: pointer;
}
.btn-text.danger { color: var(--accent-danger); }

.btn-primary {
  padding: 8px 16px; background: var(--accent);
  border: none; border-radius: 8px; color: white;
  font-size: 13px; cursor: pointer;
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
.form-field label { font-size: 13px; color: var(--text-secondary); }
.form-field input {
  padding: 10px 12px; background: var(--bg-tertiary);
  border: 1px solid var(--border); border-radius: 8px;
  color: var(--text-primary); font-size: 14px; outline: none;
}
.form-actions {
  display: flex; justify-content: flex-end;
}
</style>
