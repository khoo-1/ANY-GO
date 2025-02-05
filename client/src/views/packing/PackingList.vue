<template>
  <div class="packing-list-container">
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="店铺名称/装箱单号"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.type" placeholder="请选择" clearable>
            <el-option label="普货" value="普货" />
            <el-option label="纺织" value="纺织" />
            <el-option label="混装" value="混装" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
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
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <div class="left">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建装箱单
            </el-button>
            <el-upload
              class="upload-btn"
              :action="uploadUrl"
              :headers="uploadHeaders"
              :show-file-list="false"
              :before-upload="beforeUpload"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
            >
              <el-button>
                <el-icon><Upload /></el-icon>
                导入
              </el-button>
            </el-upload>
            <el-button :disabled="!selectedIds.length" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
            <el-button
              type="success"
              :disabled="!selectedIds.length"
              @click="handleApprove"
            >
              <el-icon><Check /></el-icon>
              批量通过
            </el-button>
            <el-button
              type="danger"
              :disabled="!selectedIds.length"
              @click="handleReject"
            >
              <el-icon><Close /></el-icon>
              批量拒绝
            </el-button>
          </div>
          <div class="right">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="table">表格</el-radio-button>
              <el-radio-button label="card">卡片</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <div v-if="viewMode === 'table'">
        <el-table
          v-loading="loading"
          :data="tableData"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="code" label="装箱单号" width="180" />
          <el-table-column prop="storeName" label="店铺名称" width="180" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="totalBoxes" label="总箱数" width="100" />
          <el-table-column prop="totalPieces" label="总件数" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="180" />
          <el-table-column label="操作" fixed="right" width="200">
            <template #default="{ row }">
              <el-button-group>
                <el-button
                  type="primary"
                  link
                  @click="handleView(row)"
                >
                  查看
                </el-button>
                <el-button
                  type="primary"
                  link
                  @click="handleEdit(row)"
                  v-if="row.status === 'pending'"
                >
                  编辑
                </el-button>
                <el-button
                  type="primary"
                  link
                  @click="handlePrint(row)"
                >
                  打印
                </el-button>
                <el-button
                  type="danger"
                  link
                  @click="handleDelete(row)"
                  v-if="row.status === 'pending'"
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
      </div>

      <div v-else class="card-view">
        <el-row :gutter="20">
          <el-col
            v-for="item in tableData"
            :key="item.id"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
          >
            <el-card class="packing-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>{{ item.code }}</span>
                  <el-tag :type="getStatusType(item.status)">
                    {{ getStatusText(item.status) }}
                  </el-tag>
                </div>
              </template>
              <div class="card-content">
                <p><label>店铺：</label>{{ item.storeName }}</p>
                <p><label>类型：</label>{{ item.type }}</p>
                <p><label>总箱数：</label>{{ item.totalBoxes }}</p>
                <p><label>总件数：</label>{{ item.totalPieces }}</p>
                <p><label>创建时间：</label>{{ item.createdAt }}</p>
              </div>
              <div class="card-footer">
                <el-button-group>
                  <el-button
                    type="primary"
                    link
                    @click="handleView(item)"
                  >
                    查看
                  </el-button>
                  <el-button
                    type="primary"
                    link
                    @click="handleEdit(item)"
                    v-if="item.status === 'pending'"
                  >
                    编辑
                  </el-button>
                  <el-button
                    type="primary"
                    link
                    @click="handlePrint(item)"
                  >
                    打印
                  </el-button>
                  <el-button
                    type="danger"
                    link
                    @click="handleDelete(item)"
                    v-if="item.status === 'pending'"
                  >
                    删除
                  </el-button>
                </el-button-group>
              </div>
            </el-card>
          </el-col>
        </el-row>

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
      </div>
    </el-card>

    <!-- 导出对话框 -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出装箱单"
      width="400px"
    >
      <el-form :model="exportForm" label-width="140px">
        <el-form-item label="包含箱子规格">
          <el-switch v-model="exportForm.includeBoxSpecs" />
        </el-form-item>
        <el-form-item label="包含商品详情">
          <el-switch v-model="exportForm.includeProductDetails" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmExport">
            确认导出
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadProps, UploadFile } from 'element-plus'
import * as packingApi from '../../api/packing'
import type { PackingList } from '../../types/packing'

const router = useRouter()
const loading = ref(false)
const viewMode = ref<'table' | 'card'>('table')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const tableData = ref<PackingList[]>([])
const selectedIds = ref<number[]>([])
const dateRange = ref<[string, string] | null>(null)
const exportDialogVisible = ref(false)

const searchForm = reactive({
  keyword: '',
  type: '',
  status: '',
  startDate: '',
  endDate: ''
})

const exportForm = reactive({
  includeBoxSpecs: true,
  includeProductDetails: true
})

// 计算上传URL和请求头
const uploadUrl = computed(() => `${import.meta.env.VITE_API_URL}/packing-lists/import`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

// 状态相关方法
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status] || status
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      pageSize: pageSize.value,
      ...searchForm
    }
    const res = await packingApi.getPackingLists(params)
    tableData.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索和重置
const handleSearch = () => {
  if (dateRange.value) {
    searchForm.startDate = dateRange.value[0]
    searchForm.endDate = dateRange.value[1]
  } else {
    searchForm.startDate = ''
    searchForm.endDate = ''
  }
  currentPage.value = 1
  loadData()
}

const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key as keyof typeof searchForm] = ''
  })
  dateRange.value = null
  currentPage.value = 1
  loadData()
}

// 表格操作
const handleSelectionChange = (selection: PackingList[]) => {
  selectedIds.value = selection.map(item => item.id!).filter(Boolean)
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadData()
}

// 上传相关
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                 file.type === 'application/vnd.ms-excel'
  if (!isExcel) {
    ElMessage.error('只能上传 Excel 文件!')
    return false
  }
  return true
}

const handleUploadSuccess = (res: any) => {
  if (res.success) {
    ElMessage.success(`导入成功: 共${res.total}条，新增${res.created}条，更新${res.updated}条`)
    loadData()
  } else {
    ElMessage.error(res.message || '导入失败')
  }
}

const handleUploadError = () => {
  ElMessage.error('导入失败')
}

// 导入处理
const handleImport = async (file: UploadFile) => {
  try {
    loading.value = true
    const formData = new FormData()
    formData.append('file', file.raw!)
    const res = await packingApi.importPackingLists(formData)
    
    if (res.success) {
      ElMessage.success(`导入成功: 共${res.total}条, 成功${res.success_count}条, 失败${res.error_count}条`)
      if (res.error_messages?.length) {
        ElMessageBox.alert(res.error_messages.join('\n'), '导入错误详情')
      }
    } else {
      ElMessage.error(res.error || '导入失败')
    }
    
    // 刷新列表
    loadData()
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  } finally {
    loading.value = false
  }
}

// 导出处理
const handleExport = async () => {
  try {
    const { value } = await ElMessageBox.confirm(
      '是否包含箱子规格信息?',
      '导出确认',
      {
        confirmButtonText: '包含',
        cancelButtonText: '不包含',
        type: 'info'
      }
    )
    
    const ids = selectedIds.value.length ? selectedIds.value : undefined
    await packingApi.exportPackingLists({
      ids: ids,
      include_box_specs: value
    })
  } catch (error) {
    if (error !== 'cancel') {
      console.error('导出失败:', error)
      ElMessage.error('导出失败')
    }
  }
}

// 批量审批处理
const handleApprove = async () => {
  if (!selectedIds.value.length) {
    ElMessage.warning('请选择要审批的装箱单')
    return
  }
  
  try {
    await ElMessageBox.confirm('确定要批量通过选中的装箱单吗？')
    await packingApi.approvePackingLists(selectedIds.value)
    ElMessage.success('操作成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审批失败:', error)
      ElMessage.error('审批失败')
    }
  }
}

// 批量拒绝处理
const handleReject = async () => {
  if (!selectedIds.value.length) {
    ElMessage.warning('请选择要拒绝的装箱单')
    return
  }
  
  try {
    await ElMessageBox.confirm('确定要批量拒绝选中的装箱单吗？')
    await packingApi.rejectPackingLists(selectedIds.value)
    ElMessage.success('操作成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('拒绝失败:', error)
      ElMessage.error('拒绝失败')
    }
  }
}

// 单个操作
const handleCreate = () => {
  router.push('/packing-lists/create')
}

const handleView = (row: PackingList) => {
  router.push(`/packing-lists/${row.id}`)
}

const handleEdit = (row: PackingList) => {
  router.push(`/packing-lists/${row.id}/edit`)
}

const handlePrint = (row: PackingList) => {
  router.push(`/packing-lists/${row.id}/print`)
}

const handleDelete = async (row: PackingList) => {
  try {
    await ElMessageBox.confirm('确定要删除该装箱单吗？')
    await packingApi.deletePackingList(row.id!)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 初始加载
loadData()
</script>

<style scoped>
.packing-list-container {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left {
  display: flex;
  gap: 10px;
}

.upload-btn {
  display: inline-block;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.card-view {
  margin-top: 20px;
}

.packing-card {
  margin-bottom: 20px;
}

.card-content {
  p {
    margin: 8px 0;
    display: flex;
    align-items: center;
  }

  label {
    color: #666;
    margin-right: 8px;
    min-width: 70px;
  }
}

.card-footer {
  margin-top: 15px;
  border-top: 1px solid #eee;
  padding-top: 15px;
  text-align: right;
}
</style> 