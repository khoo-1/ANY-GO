<template>
  <div class="user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="left">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新增用户
            </el-button>
          </div>
          <div class="right">
            <el-form :inline="true" :model="searchForm" @keyup.enter="handleSearch">
              <el-form-item>
                <el-input
                  v-model="searchForm.keyword"
                  placeholder="搜索用户名"
                  clearable
                  @clear="handleSearch"
                />
              </el-form-item>
              <el-form-item>
                <el-select
                  v-model="searchForm.role"
                  placeholder="选择角色"
                  clearable
                  @clear="handleSearch"
                >
                  <el-option label="管理员" value="admin" />
                  <el-option label="经理" value="manager" />
                  <el-option label="操作员" value="operator" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-select
                  v-model="searchForm.status"
                  placeholder="选择状态"
                  clearable
                  @clear="handleSearch"
                >
                  <el-option label="启用" value="active" />
                  <el-option label="禁用" value="inactive" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSearch">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
      >
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLoginAt" label="最后登录" width="180">
          <template #default="{ row }">
            {{ row.lastLoginAt ? new Date(row.lastLoginAt).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button
                type="primary"
                link
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                type="primary"
                link
                @click="handleResetPassword(row)"
              >
                重置密码
              </el-button>
              <el-button
                type="danger"
                link
                @click="handleDelete(row)"
                v-if="row.role !== 'admin'"
              >
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 用户表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="currentUser ? '编辑用户' : '新增用户'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item
          label="密码"
          prop="password"
          v-if="!currentUser"
        >
          <el-input
            v-model="form.password"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="经理" value="manager" />
            <el-option label="操作员" value="operator" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="重置密码"
      width="500px"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handlePasswordSubmit">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import userApi from '../../api/user'
import type { User, UserRole, UserStatus } from '../../types/user'
import type { UserQuery, UserCreateParams, UserUpdateParams } from '../../api/user'

interface User {
  id: string
  username: string
  role: string
  status: string
  lastLoginAt?: string
}

// 状态定义
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const tableData = ref<User[]>([])
const dialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const currentUser = ref<User | null>(null)
const formRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

// 表单数据
const searchForm = reactive({
  keyword: '',
  role: '',
  status: ''
})

const form = reactive({
  username: '',
  password: '',
  role: 'operator',
  status: 'active'
})

const passwordForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能小于3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
})

const passwordRules = reactive<FormRules>({
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})

// 获取用户列表
const fetchUsers = async () => {
  try {
    loading.value = true
    const params: UserQuery = {
      page: currentPage.value,
      pageSize: pageSize.value,
      ...searchForm
    }
    const { data } = await userApi.list(params)
    tableData.value = data.items
    total.value = data.pagination.total
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 事件处理方法
const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchUsers()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchUsers()
}

const handleCreate = () => {
  currentUser.value = null
  form.username = ''
  form.password = ''
  form.role = 'operator'
  form.status = 'active'
  dialogVisible.value = true
}

const handleEdit = (row: User) => {
  currentUser.value = row
  form.username = row.username
  form.role = row.role
  form.status = row.status
  dialogVisible.value = true
}

const handleDelete = (row: User) => {
  ElMessageBox.confirm(
    '确定要删除该用户吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await userApi.delete(row.id)
      ElMessage.success('删除成功')
      fetchUsers()
    } catch (error) {
      console.error('删除用户失败:', error)
      ElMessage.error('删除用户失败')
    }
  })
}

const handleResetPassword = (row: User) => {
  currentUser.value = row
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (currentUser.value) {
          const params: UserUpdateParams = {
            username: form.username,
            role: form.role as UserRole,
            status: form.status as UserStatus
          }
          await userApi.update(currentUser.value.id, params)
          ElMessage.success('更新成功')
        } else {
          const params: UserCreateParams = {
            username: form.username,
            password: form.password,
            role: form.role as UserRole,
            status: form.status as UserStatus
          }
          await userApi.create(params)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchUsers()
      } catch (error) {
        console.error('保存用户失败:', error)
        ElMessage.error('保存用户失败')
      }
    }
  })
}

const handlePasswordSubmit = async () => {
  if (!passwordFormRef.value || !currentUser.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await userApi.resetPassword(currentUser.value.id, {
          newPassword: passwordForm.newPassword
        })
        ElMessage.success('密码重置成功')
        passwordDialogVisible.value = false
      } catch (error) {
        console.error('重置密码失败:', error)
        ElMessage.error('重置密码失败')
      }
    }
  })
}

// 工具方法
const getRoleType = (role: string) => {
  const types = {
    admin: 'danger',
    manager: 'warning',
    operator: 'info'
  }
  return types[role as keyof typeof types]
}

const getRoleText = (role: string) => {
  const texts = {
    admin: '管理员',
    manager: '经理',
    operator: '操作员'
  }
  return texts[role as keyof typeof texts]
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-card__header) {
  padding: 10px 20px;
}

:deep(.el-form--inline .el-form-item) {
  margin-bottom: 0;
}
</style> 