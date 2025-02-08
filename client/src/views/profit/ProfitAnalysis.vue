<template>
  <div class="page-container">
    <div class="page-header">
      <h2>利润分析</h2>
      <div class="header-actions">
        <el-button type="primary" @click="calculateAnalysis">生成分析</el-button>
      </div>
    </div>

    <!-- 分析条件 -->
    <el-form :model="searchForm" inline>
      <el-form-item label="分析类型">
        <el-select v-model="searchForm.type">
          <el-option label="日度分析" value="daily" />
          <el-option label="周度分析" value="weekly" />
          <el-option label="月度分析" value="monthly" />
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

    <!-- 利润总览 -->
    <el-row :gutter="20" class="dashboard-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>总销售额</span>
              <el-tag>元</el-tag>
            </div>
          </template>
          <div class="card-value">{{ formatCurrency(overview.totalSales) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>总成本</span>
              <el-tag>元</el-tag>
            </div>
          </template>
          <div class="card-value">{{ formatCurrency(overview.totalCost) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>毛利润</span>
              <el-tag>元</el-tag>
            </div>
          </template>
          <div class="card-value">{{ formatCurrency(overview.grossProfit) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>净利润</span>
              <el-tag>元</el-tag>
            </div>
          </template>
          <div class="card-value">{{ formatCurrency(overview.netProfit) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 利润趋势和品类分布 -->
    <el-row :gutter="20" class="analysis-charts">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>利润趋势</span>
            </div>
          </template>
          <div ref="trendChart" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>品类利润分布</span>
            </div>
          </template>
          <div ref="categoryChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 商品利润排名 -->
    <el-row :gutter="20" class="analysis-tables">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>利润最高商品</span>
            </div>
          </template>
          <el-table :data="topProducts" border stripe>
            <el-table-column prop="productSku" label="SKU" width="120" />
            <el-table-column prop="productName" label="商品名称" />
            <el-table-column prop="salesQuantity" label="销量" width="100" />
            <el-table-column prop="grossProfit" label="毛利润">
              <template #default="{ row }">
                {{ formatCurrency(row.grossProfit) }}
              </template>
            </el-table-column>
            <el-table-column prop="grossProfitRate" label="毛利率">
              <template #default="{ row }">
                {{ (row.grossProfitRate * 100).toFixed(2) }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>利润最低商品</span>
            </div>
          </template>
          <el-table :data="bottomProducts" border stripe>
            <el-table-column prop="productSku" label="SKU" width="120" />
            <el-table-column prop="productName" label="商品名称" />
            <el-table-column prop="salesQuantity" label="销量" width="100" />
            <el-table-column prop="grossProfit" label="毛利润">
              <template #default="{ row }">
                {{ formatCurrency(row.grossProfit) }}
              </template>
            </el-table-column>
            <el-table-column prop="grossProfitRate" label="毛利率">
              <template #default="{ row }">
                {{ (row.grossProfitRate * 100).toFixed(2) }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 品类分析表格 -->
    <el-card shadow="hover" class="mt-4">
      <template #header>
        <div class="card-header">
          <span>品类分析</span>
        </div>
      </template>
      <el-table :data="categoryAnalysis" border stripe>
        <el-table-column prop="category" label="品类" />
        <el-table-column prop="totalProducts" label="商品数" />
        <el-table-column prop="totalOrders" label="订单数" />
        <el-table-column prop="salesAmount" label="销售额">
          <template #default="{ row }">
            {{ formatCurrency(row.salesAmount) }}
          </template>
        </el-table-column>
        <el-table-column prop="grossProfit" label="毛利润">
          <template #default="{ row }">
            {{ formatCurrency(row.grossProfit) }}
          </template>
        </el-table-column>
        <el-table-column prop="netProfit" label="净利润">
          <template #default="{ row }">
            {{ formatCurrency(row.netProfit) }}
          </template>
        </el-table-column>
        <el-table-column prop="grossProfitRate" label="毛利率">
          <template #default="{ row }">
            {{ (row.grossProfitRate * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="netProfitRate" label="净利率">
          <template #default="{ row }">
            {{ (row.netProfitRate * 100).toFixed(2) }}%
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 生成分析对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="生成利润分析"
      width="500px"
    >
      <el-form :model="analysisForm" label-width="100px">
        <el-form-item label="分析类型">
          <el-select v-model="analysisForm.type">
            <el-option label="日度分析" value="daily" />
            <el-option label="周度分析" value="weekly" />
            <el-option label="月度分析" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="分析日期">
          <el-date-picker
            v-model="analysisForm.date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleGenerateAnalysis">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import profitApi from '@/api/profit'
import { formatCurrency } from '@/utils/format'

// 搜索表单
const searchForm = ref({
  type: 'daily',
  dateRange: [] as string[]
})

// 总览数据
const overview = ref({
  totalSales: 0,
  totalCost: 0,
  grossProfit: 0,
  netProfit: 0,
  grossProfitRate: 0,
  netProfitRate: 0
})

// 商品利润排名
const topProducts = ref([])
const bottomProducts = ref([])

// 品类分析数据
const categoryAnalysis = ref([])

// 图表实例
let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null

// 对话框控制
const dialogVisible = ref(false)
const analysisForm = ref({
  type: 'daily',
  date: ''
})

// 初始化图表
const initCharts = () => {
  const trendChartDom = document.querySelector('.trend-chart') as HTMLElement
  const categoryChartDom = document.querySelector('.category-chart') as HTMLElement
  
  trendChart = echarts.init(trendChartDom)
  categoryChart = echarts.init(categoryChartDom)
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    trendChart?.resize()
    categoryChart?.resize()
  })
}

// 更新趋势图表
const updateTrendChart = (data: any) => {
  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['销售额', '毛利润', '净利润']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '销售额',
        type: 'line',
        data: data.sales
      },
      {
        name: '毛利润',
        type: 'line',
        data: data.grossProfit
      },
      {
        name: '净利润',
        type: 'line',
        data: data.netProfit
      }
    ]
  }
  
  trendChart?.setOption(option)
}

// 更新品类分布图表
const updateCategoryChart = (data: any) => {
  const option: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      type: 'scroll'
    },
    series: [
      {
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        data: data.map((item: any) => ({
          name: item.category,
          value: item.grossProfit
        }))
      }
    ]
  }
  
  categoryChart?.setOption(option)
}

// 查询数据
const handleSearch = async () => {
  try {
    const [startDate, endDate] = searchForm.value.dateRange
    const params = {
      type: searchForm.value.type,
      startDate,
      endDate
    }
    
    const [analysisData, categoryData, productData] = await Promise.all([
      profitApi.getAnalysis(params),
      profitApi.getCategoryAnalysis(params),
      profitApi.getProductAnalysis(params)
    ])
    
    overview.value = analysisData
    categoryAnalysis.value = categoryData
    topProducts.value = productData.topProducts
    bottomProducts.value = productData.bottomProducts
    
    // 更新图表
    nextTick(() => {
      updateTrendChart(analysisData.trend)
      updateCategoryChart(categoryData)
    })
  } catch (error) {
    ElMessage.error('获取分析数据失败')
  }
}

// 重置查询
const handleReset = () => {
  searchForm.value = {
    type: 'daily',
    dateRange: []
  }
  handleSearch()
}

// 显示生成分析对话框
const calculateAnalysis = () => {
  dialogVisible.value = true
  analysisForm.value = {
    type: 'daily',
    date: new Date().toISOString().split('T')[0]
  }
}

// 生成分析数据
const handleGenerateAnalysis = async () => {
  try {
    await profitApi.calculateAnalysis(
      analysisForm.value.date,
      analysisForm.value.type
    )
    ElMessage.success('分析数据生成成功')
    dialogVisible.value = false
    handleSearch()
  } catch (error) {
    ElMessage.error('生成分析数据失败')
  }
}

// 组件挂载时初始化
onMounted(() => {
  initCharts()
  handleSearch()
})
</script>

<style scoped>
.dashboard-cards {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  color: #409EFF;
}

.analysis-charts {
  margin-bottom: 20px;
}

.analysis-tables {
  margin-bottom: 20px;
}

.mt-4 {
  margin-top: 16px;
}
</style> 