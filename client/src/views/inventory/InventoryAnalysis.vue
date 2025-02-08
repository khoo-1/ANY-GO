<template>
  <div class="page-container">
    <div class="page-header">
      <h2>库存分析</h2>
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

    <!-- 库存总览 -->
    <el-row :gutter="20" class="dashboard-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>商品总数</span>
              <el-tag>件</el-tag>
            </div>
          </template>
          <div class="card-value">{{ overview.totalProducts }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>库存总量</span>
              <el-tag>件</el-tag>
            </div>
          </template>
          <div class="card-value">{{ overview.totalQuantity }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>库存总值</span>
              <el-tag>元</el-tag>
            </div>
          </template>
          <div class="card-value">{{ formatCurrency(overview.totalValue) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>周转天数</span>
              <el-tag>天</el-tag>
            </div>
          </template>
          <div class="card-value">{{ overview.turnoverDays.toFixed(1) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 库存健康度 -->
    <el-row :gutter="20" class="analysis-charts">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>库存健康度分布</span>
            </div>
          </template>
          <div ref="healthChart" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>周转率趋势</span>
            </div>
          </template>
          <div ref="turnoverChart" style="height: 300px"></div>
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
        <el-table-column prop="totalStock" label="库存量" />
        <el-table-column prop="totalValue" label="库存金额">
          <template #default="{ row }">
            {{ formatCurrency(row.totalValue) }}
          </template>
        </el-table-column>
        <el-table-column prop="turnoverRate" label="周转率">
          <template #default="{ row }">
            {{ row.turnoverRate.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="turnoverDays" label="周转天数">
          <template #default="{ row }">
            {{ row.turnoverDays.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column label="库存结构">
          <template #default="{ row }">
            <el-tooltip effect="dark" placement="top">
              <template #content>
                <div>动销商品: {{ row.activeProducts }}</div>
                <div>呆滞商品: {{ row.inactiveProducts }}</div>
                <div>缺货商品: {{ row.stockoutProducts }}</div>
                <div>积压商品: {{ row.overstockProducts }}</div>
              </template>
              <el-progress :percentage="getHealthyPercentage(row)" :format="() => ''" />
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 生成分析对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="生成库存分析"
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
import inventoryApi from '@/api/inventory'
import { formatCurrency } from '@/utils/format'

// 搜索表单
const searchForm = ref({
  type: 'daily',
  dateRange: [] as string[]
})

// 总览数据
const overview = ref({
  totalProducts: 0,
  totalQuantity: 0,
  totalValue: 0,
  turnoverRate: 0,
  turnoverDays: 0,
  averageInventory: 0,
  inventoryCost: 0
})

// 品类分析数据
const categoryAnalysis = ref([])

// 图表实例
let healthChart: echarts.ECharts | null = null
let turnoverChart: echarts.ECharts | null = null

// 对话框控制
const dialogVisible = ref(false)
const analysisForm = ref({
  type: 'daily',
  date: ''
})

// 初始化图表
const initCharts = () => {
  const healthChartDom = document.querySelector('.health-chart') as HTMLElement
  const turnoverChartDom = document.querySelector('.turnover-chart') as HTMLElement
  
  healthChart = echarts.init(healthChartDom)
  turnoverChart = echarts.init(turnoverChartDom)
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    healthChart?.resize()
    turnoverChart?.resize()
  })
}

// 更新健康度图表
const updateHealthChart = (data: any) => {
  const option: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: data.activeProducts, name: '动销商品' },
          { value: data.inactiveProducts, name: '呆滞商品' },
          { value: data.stockoutProducts, name: '缺货商品' },
          { value: data.overstockProducts, name: '积压商品' }
        ]
      }
    ]
  }
  
  healthChart?.setOption(option)
}

// 更新周转率图表
const updateTurnoverChart = (data: any) => {
  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: data.dates
    },
    yAxis: {
      type: 'value',
      name: '周转率'
    },
    series: [
      {
        data: data.rates,
        type: 'line',
        smooth: true
      }
    ]
  }
  
  turnoverChart?.setOption(option)
}

// 计算健康度百分比
const getHealthyPercentage = (row: any) => {
  const total = row.activeProducts + row.inactiveProducts + 
                row.stockoutProducts + row.overstockProducts
  return total > 0 ? (row.activeProducts / total * 100) : 0
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
    
    const [analysisData, categoryData] = await Promise.all([
      inventoryApi.getAnalysis(params),
      inventoryApi.getCategoryAnalysis(params)
    ])
    
    overview.value = analysisData
    categoryAnalysis.value = categoryData
    
    // 更新图表
    nextTick(() => {
      updateHealthChart(analysisData)
      updateTurnoverChart(analysisData.turnoverTrend)
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
    await inventoryApi.calculateAnalysis(
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

.mt-4 {
  margin-top: 16px;
}
</style> 