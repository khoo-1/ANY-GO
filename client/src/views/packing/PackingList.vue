<template>
  <div class="page-container">
    <div class="page-header">
      <h2>装箱单</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd">新增装箱单</el-button>
        <el-button @click="showExportDialog">导出</el-button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <el-form :model="searchForm" inline>
      <el-form-item label="关键词">
        <el-input v-model="searchForm.keyword" placeholder="装箱单编号" />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" clearable>
          <el-option label="待审核" value="待审核" />
          <el-option label="已审核" value="已审核" />
          <el-option label="已取消" value="已取消" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 数据表格 -->
    <el-table 
      v-loading="loading"
      :data="tableData"
      border
      style="width: 100%"
    >
      <el-table-column prop="code" label="装箱单编号" width="150" />
      <el-table-column label="商品数量" width="100">
        <template #default="{ row }">
          {{ row.items.length }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="创建时间" width="180">
        <template #default="{ row }">
          {{ new Date(row.createdAt).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleView(row)">查看</el-button>
          <el-button 
            v-if="row.status === '待审核'"
            link 
            type="primary" 
            @click="handleEdit(row)"
          >
            编辑
          </el-button>
          <el-popconfirm
            v-if="row.status === '待审核'"
            title="确定要删除该装箱单吗？"
            @confirm="handleDelete(row)"
          >
            <template #reference>
              <el-button link type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 导出对话框 -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出装箱单"
      width="400px"
    >
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="导出字段">
          <el-checkbox-group v-model="exportForm.fields">
            <el-checkbox label="code">装箱单编号</el-checkbox>
            <el-checkbox label="status">状态</el-checkbox>
            <el-checkbox label="items">商品明细</el-checkbox>
            <el-checkbox label="createdAt">创建时间</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleExport"
          :loading="exporting"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import packingApi from '@/api/packing'
import type { PackingList, PackingListQuery } from '@/types/packing'

const router = useRouter()

// 搜索表单
const searchForm = reactive<Partial<PackingListQuery>>({
  keyword: '',
  status: undefined
})

// 表格数据
const loading = ref(false)
const tableData = ref<PackingList[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 导出对话框
const exportDialogVisible = ref(false)
const exporting = ref(false)
const exportForm = reactive({
  fields: ['code', 'status', 'items', 'createdAt']
})

// 加载数据
async function loadData() {
  loading.value = true
  try {
    // 添加调试日志
    console.log('开始加载数据:', {
      page: page.value,
      pageSize: pageSize.value,
      ...searchForm
    })

    const response = await packingApi.list({
      page: page.value,
      pageSize: pageSize.value,
      ...searchForm
    })

    // 添加调试日志
    console.log('加载数据成功:', response)

    tableData.value = response.items
    total.value = response.total
  } catch (error: any) {
    console.error('加载数据失败:', error)
    
    // 如果是401错误，不显示错误消息（因为request.ts中已经处理了）
    if (error.response?.status !== 401) {
      ElMessage.error(
        error.response?.data?.detail || 
        error.response?.data?.message || 
        error.message || 
        '加载数据失败'
      )
    }
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(async () => {
  await loadData()
})

// 搜索
function handleSearch() {
  page.value = 1
  loadData()
}

// 重置搜索
function handleReset() {
  searchForm.keyword = ''
  searchForm.status = undefined
  handleSearch()
}

// 新增装箱单
function handleAdd() {
  router.push('/packing/create')
}

// 查看装箱单
function handleView(row: PackingList) {
  router.push(`/packing/${row.id}`)
}

// 编辑装箱单
function handleEdit(row: PackingList) {
  router.push(`/packing/${row.id}/edit`)
}

// 删除装箱单
async function handleDelete(row: PackingList) {
  try {
    await packingApi.delete(row.id)
    ElMessage.success('删除成功')
    if (tableData.value.length === 1 && page.value > 1) {
      page.value--
    }
    loadData()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

// 显示导出对话框
function showExportDialog() {
  exportDialogVisible.value = true
}

// 导出数据
async function handleExport() {
  exporting.value = true
  try {
    const response = await packingApi.export({
      fields: exportForm.fields,
      keyword: searchForm.keyword,
      status: searchForm.status
    })
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.download = `装箱单_${new Date().toLocaleDateString()}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    exportDialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

// 分页
function handleSizeChange(val: number) {
  pageSize.value = val
  loadData()
}

function handleCurrentChange(val: number) {
  page.value = val
  loadData()
}

// 获取状态标签类型
function getStatusType(status: PackingList['status']) {
  const map: Record<PackingList['status'], 'warning' | 'success' | 'info'> = {
    '待审核': 'warning',
    '已审核': 'success',
    '已取消': 'info'
  }
  return map[status]
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  margin-top: 20px;
}

:deep(.el-form--inline .el-form-item) {
  margin-right: 16px;
}
</style> 