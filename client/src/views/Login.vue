<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>{{ title }}</h2>
        </div>
      </template>
      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        label-width="0"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            :prefix-icon="User"
            class="custom-input"
            clearable
            autocomplete="username"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
            class="custom-input"
            autocomplete="current-password"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            class="login-button"
            native-type="submit"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import auth from '../api/auth'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const title = import.meta.env.VITE_APP_TITLE

const loginForm = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度至少为3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const { data } = await auth.login(loginForm)
    if (!data?.token) {
      throw new Error('登录失败：未收到有效的认证令牌')
    }
    
    userStore.setToken(data.token)
    const { data: userData } = await userStore.fetchUserInfo()
    if (!userData) {
      throw new Error('获取用户信息失败')
    }
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail
      ? Array.isArray(error.response.data.detail)
        ? error.response.data.detail.map((d: any) => d.msg).join('\n')
        : error.response.data.detail
      : error.message || '登录失败'
    
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1976d2 0%, #64b5f6 100%);
}

.login-card {
  width: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.card-header {
  text-align: center;
  margin-bottom: 20px;
}

.card-header h2 {
  color: #1976d2;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.custom-input {
  margin-bottom: 10px;
}

.login-button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  background: #1976d2;
  border: none;
  transition: background-color 0.3s ease;
}

.login-button:hover {
  background: #1565c0;
}

@media (max-width: 480px) {
  .login-card {
    width: 90%;
    margin: 0 20px;
  }
}
</style>