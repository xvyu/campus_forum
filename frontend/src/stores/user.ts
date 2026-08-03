/** 用户状态管理 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

const TOKEN_KEY = 'campus_forum_token'

export const useUserStore = defineStore('user', () => {
  const user = ref<any>(null)
  const isLoggedIn = computed(() => !!user.value)

  /** 从 localStorage 恢复 token + 拉个人信息（页面刷新时用） */
  async function initFromToken() {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) return null
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
      return res.data
    } catch {
      localStorage.removeItem(TOKEN_KEY)
      user.value = null
      return null
    }
  }

  async function fetchMe() {
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
      return res.data
    } catch {
      if (!user.value) {
        user.value = null
      }
      return null
    }
  }

  async function login(student_id: string, password: string) {
    const res = await api.post('/auth/login', { student_id, password })
    // 保存 token 到 localStorage
    const token = res.data?.token
    if (token) {
      localStorage.setItem(TOKEN_KEY, token)
    }
    user.value = {
      user_id: res.data?.user_id,
      nickname: res.data?.nickname,
      role: 1,
    }
    // 后台拉 /auth/me 补充信息
    fetchMe().catch(() => {})
    return res
  }

  async function register(data: any) {
    const res = await api.post('/auth/register', data)
    const token = res.data?.token
    if (token) {
      localStorage.setItem(TOKEN_KEY, token)
    }
    user.value = {
      user_id: res.data?.user_id,
      nickname: `树洞用户${res.data?.user_id || ''}`,
      role: 1,
    }
    fetchMe().catch(() => {})
    return res
  }

  async function logout() {
    try { await api.post('/auth/logout') } catch {}
    localStorage.removeItem(TOKEN_KEY)
    user.value = null
  }

  return { user, isLoggedIn, initFromToken, fetchMe, login, register, logout }
})
