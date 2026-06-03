<template>
  <div class="max-w-[1200px]">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-xl font-semibold text-txtp">用户管理</h1>
      <button
        class="flex items-center gap-1.5 px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover transition-colors"
        @click="openCreate"
      >
        <PlusIcon :size="16" />
        创建用户
      </button>
    </div>

    <!-- 搜索栏 -->
    <div class="mb-4">
      <div class="relative w-[280px]">
        <SearchIcon :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-txtm" />
        <input
          v-model="searchQuery"
          placeholder="搜索用户..."
          class="w-full h-9 pl-9 pr-3 bg-card border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent-hover transition-colors"
          @input="onSearch"
        />
      </div>
    </div>

    <!-- 用户表格 -->
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
          <tr v-for="user in users" :key="user.id" class="hover:bg-hover transition-colors">
            <td class="px-4 py-3 border-t border-borderc text-txts">{{ user.id }}</td>
            <td class="px-4 py-3 border-t border-borderc text-txtp">{{ user.username }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <span class="px-2 py-0.5 rounded text-xs font-medium" :class="roleClass(user.role)">{{ roleLabel(user.role) }}</span>
            </td>
            <td class="px-4 py-3 border-t border-borderc">
              <!-- 表格行内状态 toggle -->
              <button
                class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors cursor-pointer"
                :class="user.is_active ? 'bg-accent' : 'bg-txtm/30'"
                @click="toggleStatus(user)"
              >
                <span
                  class="inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform"
                  :class="user.is_active ? 'translate-x-[18px]' : 'translate-x-[2px]'"
                />
              </button>
            </td>
            <td class="px-4 py-3 border-t border-borderc text-txts">{{ formatDate(user.created_at) }}</td>
            <td class="px-4 py-3 border-t border-borderc">
              <div class="flex items-center gap-2">
                <button
                  class="px-2 py-1 bg-transparent border-none text-accent text-[13px] cursor-pointer hover:text-accent-hover transition-colors"
                  @click="openEdit(user)"
                >
                  编辑
                </button>
                <button
                  class="px-2 py-1 bg-transparent border-none text-danger text-[13px] cursor-pointer hover:text-danger/80 transition-colors"
                  @click="confirmDelete(user)"
                >
                  删除
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-txtm text-sm">暂无用户</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建/编辑用户弹窗 -->
    <div v-if="showModal" class="fixed inset-0 bg-black/70 flex items-center justify-center z-[1000]" @click.self="closeModal">
      <div class="bg-card border border-borderc rounded-card p-6 w-[440px]">
        <h3 class="text-base font-semibold text-txtp mb-4">{{ editingUser ? '编辑用户' : '创建新用户' }}</h3>

        <div class="flex flex-col gap-1.5 mb-3">
          <label class="text-[13px] text-txts">用户名</label>
          <input
            v-model="form.username"
            placeholder="输入用户名"
            class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors"
          />
        </div>

        <div class="flex flex-col gap-1.5 mb-3">
          <label class="text-[13px] text-txts">密码{{ editingUser ? '（留空表示不修改）' : '' }}</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="输入密码"
            class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors"
          />
        </div>

        <div class="flex flex-col gap-1.5 mb-3">
          <label class="text-[13px] text-txts">确认密码</label>
          <input
            v-model="form.confirmPassword"
            type="password"
            placeholder="再次输入密码"
            class="h-9 px-3 bg-active border border-borderc rounded-btn text-txtp text-sm outline-none focus:border-accent transition-colors"
            :class="passwordMismatch ? 'border-danger' : ''"
          />
          <p v-if="passwordMismatch" class="text-[12px] text-danger">两次输入的密码不一致</p>
        </div>

        <div class="flex flex-col gap-1.5 mb-3">
          <label class="text-[13px] text-txts">角色</label>
          <div class="flex items-center gap-4 mt-1">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.role" type="radio" value="admin" class="accent-accent w-4 h-4 cursor-pointer" />
              <span class="text-sm text-txtp">管理员</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.role" type="radio" value="leader" class="accent-accent w-4 h-4 cursor-pointer" />
              <span class="text-sm text-txtp">组长</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.role" type="radio" value="user" class="accent-accent w-4 h-4 cursor-pointer" />
              <span class="text-sm text-txtp">普通用户</span>
            </label>
          </div>
        </div>

        <div class="flex flex-col gap-1.5 mb-4">
          <label class="text-[13px] text-txts">激活状态</label>
          <div class="flex items-center gap-3 mt-1">
            <button
              class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors cursor-pointer"
              :class="form.is_active ? 'bg-accent' : 'bg-txtm/30'"
              @click="form.is_active = !form.is_active"
            >
              <span
                class="inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform"
                :class="form.is_active ? 'translate-x-[18px]' : 'translate-x-[2px]'"
              />
            </button>
            <span class="text-sm text-txts">{{ form.is_active ? '已激活' : '已禁用' }}</span>
          </div>
        </div>

        <div class="flex justify-end gap-3">
          <button
            class="px-4 h-9 bg-active border border-borderc rounded-btn text-txts text-[13px] cursor-pointer hover:bg-hover transition-colors"
            @click="closeModal"
          >
            取消
          </button>
          <button
            class="px-4 h-9 bg-accent border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-accent-hover transition-colors"
            :disabled="!canSubmit"
            @click="submit"
          >
            {{ editingUser ? '保存' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/70 flex items-center justify-center z-[1000]" @click.self="showDeleteConfirm = false">
      <div class="bg-card border border-borderc rounded-card p-6 w-[400px]">
        <h3 class="text-base font-semibold text-txtp mb-2">确认删除</h3>
        <p class="text-sm text-txts mb-6">删除后该用户的所有数据将无法恢复，是否继续？</p>
        <div class="flex justify-end gap-3">
          <button
            class="px-4 h-9 bg-active border border-borderc rounded-btn text-txts text-[13px] cursor-pointer hover:bg-hover transition-colors"
            @click="showDeleteConfirm = false"
          >
            取消
          </button>
          <button
            class="px-4 h-9 bg-danger border-none rounded-btn text-white text-[13px] cursor-pointer hover:bg-danger/80 transition-colors"
            @click="doDelete"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Search } from 'lucide-vue-next'
import dayjs from 'dayjs'
import api from '@/api'
import type { AdminUser } from '@/types'

const PlusIcon = Plus
const SearchIcon = Search

const users = ref<AdminUser[]>([])
const searchQuery = ref('')

// 弹窗状态
const showModal = ref(false)
const editingUser = ref<AdminUser | null>(null)
const form = ref({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'user' as 'user' | 'leader' | 'admin',
  is_active: true,
})

// 删除确认
const showDeleteConfirm = ref(false)
const deletingUser = ref<AdminUser | null>(null)

const passwordMismatch = computed(() => {
  if (!form.value.confirmPassword) return false
  return form.value.password !== form.value.confirmPassword
})

const canSubmit = computed(() => {
  if (!form.value.username) return false
  if (!editingUser.value) {
    // 创建时必须填写密码和确认密码
    if (!form.value.password || !form.value.confirmPassword) return false
  }
  if (form.value.confirmPassword && form.value.password !== form.value.confirmPassword) return false
  return true
})

async function fetchUsers() {
  try {
    const params: Record<string, string> = {}
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    const res = await api.get('/admin/users', { params })
    users.value = res.data
  } catch (e: any) {
    alert(e.response?.data?.detail || '获取用户列表失败')
  }
}

let searchTimer: ReturnType<typeof setTimeout> | null = null
function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    fetchUsers()
  }, 300)
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

function openCreate() {
  editingUser.value = null
  form.value = { username: '', password: '', confirmPassword: '', role: 'user', is_active: true }
  showModal.value = true
}

function openEdit(user: AdminUser) {
  editingUser.value = user
  form.value = {
    username: user.username,
    password: '',
    confirmPassword: '',
    role: user.role,
    is_active: user.is_active,
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingUser.value = null
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

async function submit() {
  if (!canSubmit.value) return

  const payload: Record<string, any> = {
    username: form.value.username,
    role: form.value.role,
    is_active: form.value.is_active,
  }

  if (form.value.password) {
    payload.password = form.value.password
  }

  try {
    if (editingUser.value) {
      await api.put(`/admin/users/${editingUser.value.id}`, payload)
    } else {
      await api.post('/admin/users', {
        username: form.value.username,
        password: form.value.password,
        role: form.value.role,
      })
    }
    closeModal()
    await fetchUsers()
  } catch (e: any) {
    alert(e.response?.data?.detail || (editingUser.value ? '保存失败' : '创建失败'))
  }
}

function confirmDelete(user: AdminUser) {
  deletingUser.value = user
  showDeleteConfirm.value = true
}

async function doDelete() {
  if (!deletingUser.value) return
  try {
    await api.delete(`/admin/users/${deletingUser.value.id}`)
    showDeleteConfirm.value = false
    deletingUser.value = null
    await fetchUsers()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

onMounted(fetchUsers)
</script>
