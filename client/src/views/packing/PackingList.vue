<template>
  <div class="page-container">
    <div class="page-header">
      <h2>装箱单列表</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd">新增装箱单</el-button>
        <el-button @click="handleImport">导入</el-button>
        <el-button @click="showExportDialog">导出</el-button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <el-form :model="searchForm" inline>
      <el-form-item label="关键词">
        <el-input v-model="searchForm.keyword" placeholder="店铺名称" />
      </el-form-item>
      <el-form-item label="类型">
        <el-select v-model="searchForm.type" clearable>
          <el-option label="普货" value="普货" />
          <el-option label="纺织" value="纺织" />
          <el-option label="混装" value="混装" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" clearable>
          <el-option label="待审核" value="pending" />
          <el-option label="已审核" value="approved" />
        </el-select>
      </el-form-item>
      <el-form-item label="日期">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />
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
      <el-table-column prop="storeName" label="店铺名称" min-width="150" />
      <el-table-column prop="type" label="类型" width="100" />
      <el-table-column label="箱数/件数" width="120">
        <template #default="{ row }">
          {{ row.totalBoxes }} / {{ row.totalPieces }}
        </template>
      </el-table-column>
      <el-table-column label="重量/体积" width="150">
        <template #default="{ row }">
          {{ row.totalWeight.toFixed(2) }}kg / {{ row.totalVolume.toFixed(2) }}m³
        </template>
      </el-table-column>
      <el-table-column prop="totalValue" label="总价值" width="120">
        <template #default="{ row }">
          ¥{{ row.totalValue.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'approved' ? 'success' : ''">
            {{ row.status === 'approved' ? '已审核' : '待审核' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="创建时间" width="180">
        <template #default="{ row }">
          {{ new Date(row.createdAt).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleView(row)">查看</el-button>
          <el-button 
            v-if="row.status === 'pending'"
            link 
            type="primary" 
            @click="handleEdit(row)"
          >
            编辑
          </el-button>
          <el-button 
            v-if="row.status === 'pending'"
            link 
            type="success" 
            @click="handleApprove(row)"
          >
            审核
          </el-button>
          <el-popconfirm
            v-if="row.status === 'pending'"
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
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入装箱单"
      width="400px"
    >
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".xlsx,.xls"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx/xls 文件
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleImportSubmit"
          :loading="importing"
          :disabled="!importFile"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 导出对话框 -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出装箱单"
      width="400px"
    >
      <el-form :model="exportForm" label-width="120px">
        <el-form-item label="包含箱子规格">
          <el-switch v-model="exportForm.includeBoxSpecs" />
        </el-form-item>
        <el-form-item label="包含商品详情">
          <el-switch v-model="exportForm.includeProductDetails" />
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
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import type { PackingList } from '@/types/packing'
import packingApi from '@/api/packing'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  type: '',
  status: '',
  startDate: '',
  endDate: ''
})

// 日期范围
const dateRange = computed({
  get: () => {
    return searchForm.startDate && searchForm.endDate
      ? [searchForm.startDate, searchForm.endDate]
      : []
  },
  set: (val: string[]) => {
    searchForm.startDate = val[0] || ''
    searchForm.endDate = val[1] || ''
  }
})

// 表格数据
const loading = ref(false)
const tableData = ref<PackingList[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 导入相关
const importDialogVisible = ref(false)
const importing = ref(false)
const importFile = ref<File>()

// 导出相关
const exportDialogVisible = ref(false)
const exporting = ref(false)
const exportForm = reactive({
  includeBoxSpecs: true,
  includeProductDetails: true
})

// 初始化
onMounted(() => {
  loadData()
})

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const res = await packingApi.list({
      page: page.value,
      pageSize: pageSize.value,
      ...searchForm
    })
    tableData.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
function handleSearch() {
  page.value = 1
  loadData()
}

// 重置搜索
function handleReset() {
  Object.assign(searchForm, {
    keyword: '',
    type: '',
    status: '',
    startDate: '',
    endDate: ''
  })
  handleSearch()
}

// 新增装箱单
function handleAdd() {
  router.push('/packing-lists/create')
}

// 查看装箱单
function handleView(row: PackingList) {
  router.push(`/packing-lists/${row.id}`)
}

// 编辑装箱单
function handleEdit(row: PackingList) {
  router.push(`/packing-lists/${row.id}/edit`)
}

// 审核装箱单
async function handleApprove(row: PackingList) {
  try {
    await packingApi.approve(row.id!)
    ElMessage.success('审核成功')
    loadData()
  } catch (error) {
    console.error('审核失败:', error)
    ElMessage.error('审核失败')
  }
}

// 删除装箱单
async function handleDelete(row: PackingList) {
  try {
    await packingApi.delete(row.id!)
    ElMessage.success('删除成功')
    if (tableData.value.length === 1 && page.value > 1) {
      page.value--
    }
    loadData()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

// 显示导入对话框
function handleImport() {
  importDialogVisible.value = true
  importFile.value = undefined
}

// 文件选择改变
function handleFileChange(file: any) {
  importFile.value = file.raw
}

// 提交导入
async function handleImportSubmit() {
  if (!importFile.value) return
  
  importing.value = true
  try {
    const res = await packingApi.import(importFile.value)
    if (res.success) {
      ElMessage.success(`导入成功，成功导入 ${res.created} 条记录`)
      importDialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
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
    const selectedIds = tableData.value.map(item => item.id!)
    const blob = await packingApi.export({
      ids: selectedIds,
      ...exportForm
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `装箱单_${new Date().toLocaleDateString()}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    exportDialogVisible.value = false
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
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

.upload-demo {
  text-align: center;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}
</style> 