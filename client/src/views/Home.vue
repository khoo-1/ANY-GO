<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>商品总数</span>
            </div>
          </template>
          <div class="card-body">
            <h2>{{ statistics.totalProducts || 0 }}</h2>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>装箱单总数</span>
            </div>
          </template>
          <div class="card-body">
            <h2>{{ statistics.totalPackingLists || 0 }}</h2>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>本月销售额</span>
            </div>
          </template>
          <div class="card-body">
            <h2>¥{{ formatNumber(statistics.monthSales) }}</h2>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>本月利润</span>
            </div>
          </template>
          <div class="card-body">
            <h2>¥{{ formatNumber(statistics.monthProfit) }}</h2>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>销售趋势</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="salesChart" class="chart"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>利润趋势</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="profitChart" class="chart"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import request from '../utils/request'

const statistics = ref({
  totalProducts: 0,
  totalPackingLists: 0,
  monthSales: 0,
  monthProfit: 0
})

const salesChart = ref<HTMLElement | null>(null)
const profitChart = ref<HTMLElement | null>(null)
let salesChartInstance: echarts.ECharts | null = null
let profitChartInstance: echarts.ECharts | null = null

const formatNumber = (num: number) => {
  return num?.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }) || '0.00'
}

const initCharts = () => {
  if (salesChart.value && profitChart.value) {
    salesChartInstance = echarts.init(salesChart.value)
    profitChartInstance = echarts.init(profitChart.value)
    
    const salesOption = {
      title: {
        text: '近30天销售趋势'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: []
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '销售额',
          type: 'line',
          data: []
        }
      ]
    }
    
    const profitOption = {
      title: {
        text: '近30天利润趋势'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: []
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '利润',
          type: 'line',
          data: []
        }
      ]
    }
    
    salesChartInstance.setOption(salesOption)
    profitChartInstance.setOption(profitOption)
  }
}

const loadData = async () => {
  try {
    const [statsRes, trendsRes] = await Promise.all([
      request.get('/dashboard/statistics'),
      request.get('/dashboard/trends')
    ])
    
    statistics.value = statsRes
    
    if (salesChartInstance && profitChartInstance) {
      salesChartInstance.setOption({
        xAxis: {
          data: trendsRes.dates
        },
        series: [{
          data: trendsRes.sales
        }]
      })
      
      profitChartInstance.setOption({
        xAxis: {
          data: trendsRes.dates
        },
        series: [{
          data: trendsRes.profits
        }]
      })
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const handleResize = () => {
  salesChartInstance?.resize()
  profitChartInstance?.resize()
}

onMounted(() => {
  initCharts()
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  salesChartInstance?.dispose()
  profitChartInstance?.dispose()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.chart-row {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-body {
  text-align: center;
}

.card-body h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.chart-container {
  height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}
</style> 