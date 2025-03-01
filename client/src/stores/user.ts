import { defineStore } from 'pinia'
import { ref } from 'vue'
import authApi from '../api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const username = ref<string | null>(null)
  const isLoggedIn = ref(false)

  // 动作
  const login = async (loginData: { username: string; password: string }) => {
    try {
      const response = await authApi.login(loginData)
      username.value = response.username
      isLoggedIn.value = true
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
      username.value = null
      isLoggedIn.value = false
      return true
    } catch (error) {
      console.error('登出失败:', error)
      return false
    }
  }

  const checkAuth = async () => {
    try {
      const user = await authApi.getCurrentUser()
      username.value = user.username
      isLoggedIn.value = true
      return true
    } catch (error) {
      username.value = null
      isLoggedIn.value = false
      return false
    }
  }

  return {
    // 状态
    username,
    isLoggedIn,
    // 动作
    login,
    logout,
    checkAuth
  }
}) 