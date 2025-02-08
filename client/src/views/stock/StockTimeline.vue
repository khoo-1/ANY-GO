<template>
  <div class="page-container">
    <div class="page-header">
      <h2>库存时间线</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleGenerate">生成时间线</el-button>
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
      <el-form-item label="日期范围">
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

    <!-- 数据表格 -->
    <el-table
      v-loading="loading"
      :data="tableData"
      border
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="date" label="日期" width="120" />
      <el-table-column prop="productSku" label="SKU" width="150" />
      <el-table-column prop="productName" label="商品名称" min-width="200" />
      <el-table-column prop="openingStock" label="期初库存" width="100" align="right" />
      <el-table-column prop="incoming" label="入库" width="100" align="right" />
      <el-table-column prop="outgoing" label="出库" width="100" align="right" />
      <el-table-column prop="adjustments" label="调整" width="100" align="right" />
      <el-table-column prop="inTransit" label="在途" width="100" align="right">
        <template #default="{ row }">
          <el-tooltip
            v-if="row.inTransitDetails?.length"
            :content="formatTransitDetails(row.inTransitDetails)"
            placement="top"
          >
            <span>{{ row.inTransit }}</span>
          </el-tooltip>
          <span v-else>{{ row.inTransit }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="closingStock" label="期末库存" width="100" align="right" />
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

    <!-- 生成时间线对话框 -->
    <el-dialog
      v-model="generateDialogVisible"
      title="生成库存时间线"
      width="500px"
    >
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="日期范围" required>
          <el-date-picker
            v-model="generateForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="generating"
          @click="confirmGenerate"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { Product } from '@/types/product'
import type { StockTimeline } from '@/types/stock'
import stockApi from '@/api/stock'
import productApi from '@/api/product'

// 搜索表单
const searchForm = reactive({
  productId: undefined as number | undefined,
  dateRange: [] as string[]
})

// 表格数据
const loading = ref(false)
const tableData = ref<StockTimeline[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 商品选择
const productLoading = ref(false)
const productOptions = ref<Product[]>([])

// 生成时间线
const generateDialogVisible = ref(false)
const generating = ref(false)
const generateForm = reactive({
  dateRange: [] as string[]
})

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

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const [startDate, endDate] = searchForm.dateRange
    const res = await stockApi.getTimeline({
      productId: searchForm.productId,
      startDate,
      endDate,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    tableData.value = res.data
    total.value = res.total
  } catch (error) {
    console.error('加载库存时间线失败:', error)
    ElMessage.error('加载库存时间线失败')
  } finally {
    loading.value = false
  }
}

// 处理查询
function handleSearch() {
  currentPage.value = 1
  loadData()
}

// 处理重置
function handleReset() {
  searchForm.productId = undefined
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

// 处理生成时间线
function handleGenerate() {
  generateForm.dateRange = []
  generateDialogVisible.value = true
}

async function confirmGenerate() {
  if (!generateForm.dateRange.length) {
    ElMessage.warning('请选择日期范围')
    return
  }

  generating.value = true
  try {
    const [startDate, endDate] = generateForm.dateRange
    await stockApi.generateTimeline(startDate, endDate)
    ElMessage.success('生成时间线成功')
    generateDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('生成时间线失败:', error)
    ElMessage.error('生成时间线失败')
  } finally {
    generating.value = false
  }
}

// 格式化在途明细
function formatTransitDetails(details: StockTimeline['inTransitDetails']) {
  return details
    .map(item => `装箱单#${item.packingListId}: ${item.quantity}件 (预计到货: ${item.estimatedArrival})`)
    .join('\n')
}

// 初始加载
loadData()
</script>

<style scoped>
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 