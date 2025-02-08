<template>
  <div class="page-container">
    <div class="page-header">
      <h2>销售订单</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd">新增订单</el-button>
        <el-button @click="handleExport">导出</el-button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <el-form :model="searchForm" inline>
      <el-form-item label="关键词">
        <el-input v-model="searchForm.keyword" placeholder="订单号/客户" />
      </el-form-item>
      <el-form-item label="店铺">
        <el-input v-model="searchForm.storeName" placeholder="店铺名称" />
      </el-form-item>
      <el-form-item label="平台">
        <el-select v-model="searchForm.platform" clearable>
          <el-option label="Amazon" value="amazon" />
          <el-option label="eBay" value="ebay" />
          <el-option label="Shopify" value="shopify" />
        </el-select>
      </el-form-item>
      <el-form-item label="订单状态">
        <el-select v-model="searchForm.status" clearable>
          <el-option label="待处理" value="pending" />
          <el-option label="处理中" value="processing" />
          <el-option label="已发货" value="shipped" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </el-form-item>
      <el-form-item label="支付状态">
        <el-select v-model="searchForm.paymentStatus" clearable>
          <el-option label="未支付" value="unpaid" />
          <el-option label="已支付" value="paid" />
          <el-option label="已退款" value="refunded" />
        </el-select>
      </el-form-item>
      <el-form-item label="日期范围">
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
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 数据表格 -->
    <el-table
      v-loading="loading"
      :data="tableData"
      border
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="orderNo" label="订单号" width="180" />
      <el-table-column prop="storeName" label="店铺" width="120" />
      <el-table-column prop="platform" label="平台" width="100" />
      <el-table-column prop="orderDate" label="下单日期" width="100" />
      <el-table-column prop="customerName" label="客户" width="120" />
      <el-table-column prop="total" label="总金额" width="120">
        <template #default="{ row }">
          {{ formatCurrency(row.total) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="订单状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getOrderStatusType(row.status)">
            {{ getOrderStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="paymentStatus" label="支付状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getPaymentStatusType(row.paymentStatus)">
            {{ getPaymentStatusText(row.paymentStatus) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="trackingNo" label="物流单号" width="150" />
      <el-table-column prop="operatorName" label="操作人" width="100" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="handleView(row)">查看</el-button>
          <el-button 
            v-if="row.status === 'pending'" 
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
      :title="dialogType === 'add' ? '新增订单' : '编辑订单'"
      width="80%"
    >
      <OrderForm
        v-if="dialogVisible"
        :type="dialogType"
        :data="currentOrder"
        @submit="handleSubmit"
        @cancel="dialogVisible = false"
      />
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="订单详情"
      width="80%"
    >
      <OrderDetail
        v-if="detailVisible"
        :data="currentOrder"
        @close="detailVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Order } from '@/types/sales'
import OrderForm from './components/OrderForm.vue'
import OrderDetail from './components/OrderDetail.vue'
import salesApi from '@/api/sales'
import { formatCurrency } from '@/utils/format'

// 搜索表单
const searchForm = reactive({
  keyword: '',
  storeName: '',
  platform: '',
  status: '',
  paymentStatus: '',
})

// 日期范围
const dateRange = ref<[string, string]>(['', ''])

// 表格数据
const loading = ref(false)
const tableData = ref<Order[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 对话框控制
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const detailVisible = ref(false)
const currentOrder = ref<Order | null>(null)

// 获取订单列表
const loadData = async () => {
  loading.value = true
  try {
    const [startDate, endDate] = dateRange.value
    const params = {
      ...searchForm,
      page: currentPage.value,
      pageSize: pageSize.value,
      startDate,
      endDate,
    }
    const res = await salesApi.list(params)
    tableData.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载订单列表失败:', error)
    ElMessage.error('加载订单列表失败')
  } finally {
    loading.value = false
  }
}

// 订单状态样式
const getOrderStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    shipped: 'primary',
    completed: 'success',
    cancelled: 'danger',
  }
  return map[status] || 'info'
}

// 订单状态文本
const getOrderStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消',
  }
  return map[status] || status
}

// 支付状态样式
const getPaymentStatusType = (status: string) => {
  const map: Record<string, string> = {
    unpaid: 'danger',
    paid: 'success',
    refunded: 'info',
  }
  return map[status] || 'info'
}

// 支付状态文本
const getPaymentStatusText = (status: string) => {
  const map: Record<string, string> = {
    unpaid: '未支付',
    paid: '已支付',
    refunded: '已退款',
  }
  return map[status] || status
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 重置
const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key as keyof typeof searchForm] = ''
  })
  dateRange.value = ['', '']
  currentPage.value = 1
  loadData()
}

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadData()
}

// 新增订单
const handleAdd = () => {
  currentOrder.value = null
  dialogType.value = 'add'
  dialogVisible.value = true
}

// 编辑订单
const handleEdit = (row: Order) => {
  currentOrder.value = row
  dialogType.value = 'edit'
  dialogVisible.value = true
}

// 查看订单
const handleView = (row: Order) => {
  currentOrder.value = row
  detailVisible.value = true
}

// 取消订单
const handleCancel = async (row: Order) => {
  try {
    await ElMessageBox.confirm('确认取消该订单吗？', '提示', {
      type: 'warning',
    })
    await salesApi.update(row.id, { status: 'cancelled' })
    ElMessage.success('订单已取消')
    loadData()
  } catch (error) {
    console.error('取消订单失败:', error)
  }
}

// 提交表单
const handleSubmit = async (data: any) => {
  try {
    if (dialogType.value === 'add') {
      await salesApi.create(data)
      ElMessage.success('订单创建成功')
    } else {
      await salesApi.update(currentOrder.value!.id, data)
      ElMessage.success('订单更新成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('保存订单失败:', error)
    ElMessage.error('保存订单失败')
  }
}

// 导出
const handleExport = () => {
  const [startDate, endDate] = dateRange.value
  const params = {
    ...searchForm,
    startDate,
    endDate,
  }
  salesApi.export(params)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 