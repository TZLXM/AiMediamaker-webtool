<template>
  <div class="max-w-[1200px]">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-xl font-semibold">用户管理</h1>
      <button class="flex items-center gap-1.5 px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover" @click="showCreate = true">
        <PlusIcon :size="16" />
        创建用户
      </button>
    </div>
    <div class="bg-card border border-borderc rounded-card overflow-hidden">
      <table class="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">ID</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">用户名</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">角色</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">状态</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">创建时间</th>
            <th class="text-left px-4 py-3 bg-active text-txtm uppercase tracking-wider font-medium text-xs">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td class="px-4 py-3 border-t border-borderc">{{ user.id }}</td>
            <td class="px-4 py-3 border-t border-borderc">{{ user.username }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <span class="px-2 py-0.5 rounded text-xs font-medium" :class="roleClass(user.role)">{{ roleLabel(user.role) }}</span>
            </td>
            <td class="px-4 py-3 border-t border-borderc">
              <span class="px-2 py-0.5 rounded text-xs" :class="user.is_active ? 'bg-success/15 text-success' : 'bg-txtm/15 text-txtm'">
                {{ user.is_active ? '正常' : '禁用' }}
              </span>
            </td>
            <td class="px-4 py-3 border-t border-borderc">{{ formatDate(user.created_at) }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <button class="px-2 py-1 bg-transparent border-none text-accent text-[13px] cursor-pointer" @click="toggleStatus(user)">
                {{ user.is_active ? '禁用' : '启用' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建用户弹窗 -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/70 flex items-center justify-center z-[1000]" @click.self="showCreate = false">
      <div class="bg-card border border-borderc rounded-card p-6 w-[400px]">
        <h3 class="text-base font-semibold mb-4">创建新用户</h3>
        <div class="flex flex-col gap-1.5 mb-3">
          <label class="text-[13px] text-txts">用户名</label>
          <input v-model="newUser.username" placeholder="输入用户名" class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
        </div>
        <div class="flex flex-col gap-1.5 mb-3">
          <label class="text-[13px] text-txts">密码</label>
          <input v-model="newUser.password" type="password" placeholder="输入密码" class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent" />
        </div>
        <div class="flex flex-col gap-1.5 mb-3">
          <label class="text-[13px] text-txts">角色</label>
          <select v-model="newUser.role" class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent">
            <option value="user">普通用户</option>
            <option value="leader">组长</option>
            <option value="admin">管理员</option>
          </select>
        </div>
        <div class="flex justify-end gap-3 mt-4">
          <button class="px-4 h-9 bg-active border border-borderc rounded-btn text-txts text-[13px] cursor-pointer" @click="showCreate = false">取消</button>
          <button class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover" @click="createUser">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from 'lucide-vue-next'
import dayjs from 'dayjs'
import api from '@/api'
import type { AdminUser } from '@/types'

const PlusIcon = Plus

const users = ref<AdminUser[]>([])
const showCreate = ref(false)
const newUser = ref({ username: '', password: '', role: 'user' as 'user' | 'leader' | 'admin' })

async function fetchUsers() {
  try {
    const res = await api.get('/admin/users')
    users.value = res.data
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取用户列表失败')
  }
}

function roleLabel(role: string) {
  const map: Record<string, string> = { admin: '管理员', leader: '组长', user: '普通用户' }
  return map[role] || role
}

function roleClass(role: string) {
  const map: Record<string, string> = {
    admin: 'bg-danger/15 text-danger',
    leader: 'bg-warning/15 text-warning',
    user: 'bg-accent/15 text-accent',
  }
  return map[role] || ''
}

function formatDate(d: string) {
  return dayjs(d).format('YYYY-MM-DD HH:mm')
}

async function toggleStatus(user: AdminUser) {
  try {
    await api.put(`/admin/users/${user.id}`, {
      is_active: !user.is_active,
    })
    await fetchUsers()
  } catch (e: any) {
    alert(e.response?.data?.detail || '操作失败')
  }
}

async function createUser() {
  if (!newUser.value.username || !newUser.value.password) {
    alert('请填写用户名和密码')
    return
  }
  try {
    await api.post('/admin/users', newUser.value)
    showCreate.value = false
    newUser.value = { username: '', password: '', role: 'user' }
    await fetchUsers()
  } catch (e: any) {
    alert(e.response?.data?.detail || '创建失败')
  }
}

onMounted(fetchUsers)
</script>
