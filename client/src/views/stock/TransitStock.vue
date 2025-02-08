<template>
  <div class="page-container">
    <div class="page-header">
      <h2>在途库存</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd">新增记录</el-button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <el-form :model="searchForm" inline>
      <el-form-item label="商品">
        <el-select
          v-model="searchForm.productId"
          filterable
          remote
          :remote-method="searchProducts"
          :loading="productLoading"
          clearable
          placeholder="请输入SKU或名称搜索"
        >
          <el-option
            v-for="item in productOptions"
            :key="item.id"
            :label="`${item.sku} - ${item.name}`"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="运输方式">
        <el-select v-model="searchForm.transportType" clearable>
          <el-option label="海运" value="sea" />
          <el-option label="空运" value="air" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" clearable>
          <el-option label="在途中" value="in_transit" />
          <el-option label="已到货" value="arrived" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </el-form-item>
      <el-form-item label="发货日期">
        <el-date-picker
          v-model="searchForm.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 汇总信息 -->
    <el-card class="summary-card">
      <template #header>
        <div class="card-header">
          <span>在途库存汇总</span>
          <el-button text @click="loadSummary">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </template>
      <div class="summary-content">
        <div class="summary-item">
          <span class="label">总在途数量：</span>
          <span class="value">{{ summary.total.quantity }}</span>
        </div>
        <div class="summary-item">
          <span class="label">总记录数：</span>
          <span class="value">{{ summary.total.recordCount }}</span>
        </div>
        <el-divider />
        <div class="transport-summary">
          <div class="summary-item" v-if="summary.byTransportType.sea">
            <span class="label">海运在途：</span>
            <span class="value">{{ summary.byTransportType.sea.quantity }}</span>
          </div>
          <div class="summary-item" v-if="summary.byTransportType.air">
            <span class="label">空运在途：</span>
            <span class="value">{{ summary.byTransportType.air.quantity }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-table
      v-loading="loading"
      :data="tableData"
      border
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="productSku" label="SKU" width="150" />
      <el-table-column prop="productName" label="商品名称" min-width="200" />
      <el-table-column prop="quantity" label="数量" width="100" align="right" />
      <el-table-column prop="transportType" label="运输方式" width="100">
        <template #default="{ row }">
          {{ row.transportType === 'sea' ? '海运' : '空运' }}
        </template>
      </el-table-column>
      <el-table-column prop="shippingDate" label="发货日期" width="120" />
      <el-table-column prop="estimatedArrival" label="预计到货" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'in_transit'"
            link
            type="primary"
            @click="handleArrived(row)"
          >
            标记到货
          </el-button>
          <el-button
            v-if="row.status === 'in_transit'"
            link
            type="danger"
            @click="handleCancel(row)"
          >
            取消
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="商品" prop="productId">
          <el-select
            v-model="form.productId"
            filterable
            remote
            :remote-method="searchProducts"
            :loading="productLoading"
            placeholder="请输入SKU或名称搜索"
          >
            <el-option
              v-for="item in productOptions"
              :key="item.id"
              :label="`${item.sku} - ${item.name}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="装箱单" prop="packingListId">
          <el-select
            v-model="form.packingListId"
            filterable
            remote
            :remote-method="searchPackingLists"
            :loading="packingListLoading"
            placeholder="请输入装箱单号搜索"
          >
            <el-option
              v-for="item in packingListOptions"
              :key="item.id"
              :label="`#${item.id} - ${item.storeName}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="运输方式" prop="transportType">
          <el-select v-model="form.transportType">
            <el-option label="海运" value="sea" />
            <el-option label="空运" value="air" />
          </el-select>
        </el-form-item>
        <el-form-item label="发货日期" prop="shippingDate">
          <el-date-picker
            v-model="form.shippingDate"
            type="date"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="预计到货" prop="estimatedArrival">
          <el-date-picker
            v-model="form.estimatedArrival"
            type="date"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import type { Product } from '@/types/product'
import type { PackingList } from '@/types/packing'
import type { TransitStock, TransitStockCreate, TransitSummary } from '@/types/stock'
import stockApi from '@/api/stock'
import productApi from '@/api/product'
import packingApi from '@/api/packing'

// 搜索表单
const searchForm = reactive({
  productId: undefined as number | undefined,
  transportType: undefined as 'sea' | 'air' | undefined,
  status: undefined as 'in_transit' | 'arrived' | 'cancelled' | undefined,
  dateRange: [] as string[]
})

// 表格数据
const loading = ref(false)
const tableData = ref<TransitStock[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 汇总数据
const summary = ref<TransitSummary>({
  total: { quantity: 0, recordCount: 0 },
  byTransportType: {}
})

// 商品选择
const productLoading = ref(false)
const productOptions = ref<Product[]>([])

// 装箱单选择
const packingListLoading = ref(false)
const packingListOptions = ref<PackingList[]>([])

// 表单
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const form = reactive<TransitStockCreate>({
  productId: 0,
  packingListId: 0,
  quantity: 1,
  transportType: 'sea',
  shippingDate: '',
  estimatedArrival: ''
})

const rules = {
  productId: [{ required: true, message: '请选择商品' }],
  packingListId: [{ required: true, message: '请选择装箱单' }],
  quantity: [{ required: true, message: '请输入数量' }],
  transportType: [{ required: true, message: '请选择运输方式' }]
}

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const [startDate, endDate] = searchForm.dateRange
    const res = await stockApi.getTransitStock({
      productId: searchForm.productId,
      transportType: searchForm.transportType,
      status: searchForm.status,
      startDate,
      endDate,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    tableData.value = res.data
    total.value = res.total
  } catch (error) {
    console.error('加载在途库存失败:', error)
    ElMessage.error('加载在途库存失败')
  } finally {
    loading.value = false
  }
}

// 加载汇总信息
async function loadSummary() {
  try {
    const res = await stockApi.getTransitSummary(searchForm.productId)
    summary.value = res.data
  } catch (error) {
    console.error('加载汇总信息失败:', error)
  }
}

// 搜索商品
async function searchProducts(query: string) {
  if (!query) return
  
  productLoading.value = true
  try {
    const res = await productApi.list({
      keyword: query,
      page: 1,
      pageSize: 20
    })
    productOptions.value = res.data.items
  } catch (error) {
    console.error('搜索商品失败:', error)
  } finally {
    productLoading.value = false
  }
}

// 搜索装箱单
async function searchPackingLists(query: string) {
  if (!query) return
  
  packingListLoading.value = true
  try {
    const res = await packingApi.list({
      keyword: query,
      page: 1,
      pageSize: 20
    })
    packingListOptions.value = res.data.items
  } catch (error) {
    console.error('搜索装箱单失败:', error)
  } finally {
    packingListLoading.value = false
  }
}

// 处理查询
function handleSearch() {
  currentPage.value = 1
  loadData()
  loadSummary()
}

// 处理重置
function handleReset() {
  searchForm.productId = undefined
  searchForm.transportType = undefined
  searchForm.status = undefined
  searchForm.dateRange = []
  handleSearch()
}

// 处理分页
function handleSizeChange(val: number) {
  pageSize.value = val
  loadData()
}

function handleCurrentChange(val: number) {
  currentPage.value = val
  loadData()
}

// 处理新增
function handleAdd() {
  Object.assign(form, {
    productId: 0,
    packingListId: 0,
    quantity: 1,
    transportType: 'sea',
    shippingDate: '',
    estimatedArrival: ''
  })
  dialogVisible.value = true
}

// 处理提交
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate()
  
  submitting.value = true
  try {
    await stockApi.createTransitStock(form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    handleSearch()
  } catch (error) {
    console.error('创建失败:', error)
    ElMessage.error('创建失败')
  } finally {
    submitting.value = false
  }
}

// 处理标记到货
async function handleArrived(row: TransitStock) {
  try {
    await ElMessageBox.confirm('确认将该记录标记为已到货？')
    await stockApi.updateTransitStatus(row.id, 'arrived')
    ElMessage.success('操作成功')
    handleSearch()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 处理取消
async function handleCancel(row: TransitStock) {
  try {
    await ElMessageBox.confirm('确认取消该在途记录？', '提示', {
      type: 'warning'
    })
    await stockApi.updateTransitStatus(row.id, 'cancelled')
    ElMessage.success('操作成功')
    handleSearch()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 获取状态类型
function getStatusType(status: string) {
  const map: Record<string, string> = {
    in_transit: 'warning',
    arrived: 'success',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

// 获取状态文本
function getStatusText(status: string) {
  const map: Record<string, string> = {
    in_transit: '在途中',
    arrived: '已到货',
    cancelled: '已取消'
  }
  return map[status] || status
}

// 初始加载
loadData()
loadSummary()
</script>

<style scoped>
.summary-card {
  margin: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-content {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-item .label {
  color: #666;
}

.summary-item .value {
  font-size: 16px;
  font-weight: bold;
  color: #409EFF;
}

.transport-summary {
  display: flex;
  gap: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 