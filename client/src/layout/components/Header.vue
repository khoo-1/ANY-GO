<template>
  <div class="header">
    <div class="left">
      <el-button
        :icon="isCollapse ? 'Expand' : 'Fold'"
        @click="toggleSidebar"
      />
      <h2 class="title">ANY-GO 跨境电商协作平台</h2>
    </div>
    
    <div class="right">
      <el-dropdown @command="handleCommand">
        <span class="user-info">
          <el-icon><User /></el-icon>
          {{ userStore.username }}
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 定义props
const props = defineProps<{
  isCollapse: boolean
}>()

// 定义事件
const emit = defineEmits<{
  (e: 'update:isCollapse', value: boolean): void
}>()

// 切换侧边栏
const toggleSidebar = () => {
  emit('update:isCollapse', !props.isCollapse)
}

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      const success = await userStore.logout()
      if (success) {
        ElMessage.success('退出登录成功')
        router.push('/login')
      }
    } catch (error) {
      console.error('退出登录失败:', error)
      ElMessage.error('退出登录失败')
    }
  }
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
}

.left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}
</style> 