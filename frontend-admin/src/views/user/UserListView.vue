<template>
  <div class="page-container">
    <div class="page-header">
      <h1>用户管理</h1>
      <button class="btn-primary" @click="showCreate = true">
        <PlusIcon :size="16" />
        创建用户
      </button>
    </div>
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>角色</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>
              <span class="tag" :class="user.role">{{ roleLabel(user.role) }}</span>
            </td>
            <td>
              <span class="status-dot" :class="user.is_active ? 'active' : 'inactive'">
                {{ user.is_active ? '正常' : '禁用' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <button class="btn-text" @click="toggleStatus(user)">
                {{ user.is_active ? '禁用' : '启用' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建用户弹窗 -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal-card">
        <h3>创建新用户</h3>
        <div class="form-field">
          <label>用户名</label>
          <input v-model="newUser.username" placeholder="输入用户名" />
        </div>
        <div class="form-field">
          <label>密码</label>
          <input v-model="newUser.password" type="password" placeholder="输入密码" />
        </div>
        <div class="form-field">
          <label>角色</label>
          <select v-model="newUser.role">
            <option value="user">普通用户</option>
            <option value="leader">组长</option>
            <option value="admin">管理员</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showCreate = false">取消</button>
          <button class="btn-primary" @click="createUser">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from 'lucide-vue-next'
import dayjs from 'dayjs'
// import api from '@/api'
import type { AdminUser } from '@/types'

const PlusIcon = Plus

const users = ref<AdminUser[]>([])
const showCreate = ref(false)
const newUser = ref({ username: '', password: '', role: 'user' as 'user' | 'leader' | 'admin' })

async function fetchUsers() {
  // TODO: 接入获取用户列表API
}

function roleLabel(role: string) {
  const map: Record<string, string> = { admin: '管理员', leader: '组长', user: '普通用户' }
  return map[role] || role
}

function formatDate(d: string) {
  return dayjs(d).format('YYYY-MM-DD HH:mm')
}

async function toggleStatus(_user: AdminUser) {
  // TODO: 接入启用/禁用API
}

async function createUser() {
  // TODO: 接入创建用户API
  showCreate.value = false
  fetchUsers()
}

onMounted(fetchUsers)
</script>

<style scoped>
.page-container { max-width: 1200px; }
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-header h1 { font-size: 20px; font-weight: 600; }

.btn-primary {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px; background: var(--color-accent);
  border: none; border-radius: 8px; color: white;
  font-size: 13px; cursor: pointer;
}

.table-container {
  background: var(--color-card);
  border: 1px solid var(--color-borderc);
  border-radius: 12px;
  overflow: hidden;
}

.data-table {
  width: 100%; border-collapse: collapse; font-size: 14px;
}
.data-table th {
  text-align: left; padding: 12px 16px;
  background: var(--color-active); color: var(--color-txts);
  font-weight: 500; font-size: 13px;
}
.data-table td {
  padding: 12px 16px; border-top: 1px solid var(--color-borderc);
}

.tag {
  padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500;
}
.tag.admin { background: rgba(239, 68, 68, 0.15); color: var(--color-danger); }
.tag.leader { background: rgba(245, 158, 11, 0.15); color: var(--color-warning); }
.tag.user { background: rgba(99, 102, 241, 0.15); color: var(--color-accent); }

.status-dot {
  padding: 2px 8px; border-radius: 4px; font-size: 12px;
}
.status-dot.active { background: rgba(34, 197, 94, 0.15); color: var(--color-success); }
.status-dot.inactive { background: rgba(113, 113, 122, 0.15); color: var(--color-txtm); }

.btn-text {
  padding: 4px 8px; background: transparent; border: none;
  color: var(--color-accent); font-size: 13px; cursor: pointer;
}

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0, 0, 0, 0.7);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-card {
  background: var(--color-card); border: 1px solid var(--color-borderc);
  border-radius: 12px; padding: 24px; width: 400px;
}
.modal-card h3 { font-size: 16px; margin-bottom: 16px; }
.form-field {
  display: flex; flex-direction: column; gap: 6px;
  margin-bottom: 12px;
}
.form-field label { font-size: 13px; color: var(--color-txts); }
.form-field input, .form-field select {
  padding: 10px 12px; background: var(--color-active);
  border: 1px solid var(--color-borderc); border-radius: 8px;
  color: var(--color-txtp); font-size: 14px; outline: none;
}
.modal-actions {
  display: flex; justify-content: flex-end; gap: 12px;
  margin-top: 16px;
}
.btn-secondary {
  padding: 8px 16px; background: var(--color-active);
  border: 1px solid var(--color-borderc); border-radius: 8px;
  color: var(--color-txts); font-size: 13px; cursor: pointer;
}
</style>
