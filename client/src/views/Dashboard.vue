<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>产品总数</span>
            </div>
          </template>
          <div class="card-content">
            <el-statistic :value="0">
              <template #title>
                <div style="display: inline-flex; align-items: center">
                  产品种类
                  <el-icon style="margin-left: 4px">
                    <Goods />
                  </el-icon>
                </div>
              </template>
            </el-statistic>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>装箱单数量</span>
            </div>
          </template>
          <div class="card-content">
            <el-statistic :value="0">
              <template #title>
                <div style="display: inline-flex; align-items: center">
                  装箱单
                  <el-icon style="margin-left: 4px">
                    <Document />
                  </el-icon>
                </div>
              </template>
            </el-statistic>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>系统用户</span>
            </div>
          </template>
          <div class="card-content">
            <el-statistic :value="0">
              <template #title>
                <div style="display: inline-flex; align-items: center">
                  用户数
                  <el-icon style="margin-left: 4px">
                    <User />
                  </el-icon>
                </div>
              </template>
            </el-statistic>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
            </div>
          </template>
          <div class="card-content">
            <el-timeline>
              <el-timeline-item
                v-for="(activity, index) in activities"
                :key="index"
                :timestamp="activity.timestamp"
              >
                {{ activity.content }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="card-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-button type="primary" :icon="Plus" @click="handleQuickAction('product')">
                  新增产品
                </el-button>
              </el-col>
              <el-col :span="8">
                <el-button type="success" :icon="Document" @click="handleQuickAction('packing')">
                  创建装箱单
                </el-button>
              </el-col>
              <el-col :span="8">
                <el-button type="info" :icon="Search" @click="handleQuickAction('search')">
                  库存查询
                </el-button>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Document, Goods, User, Plus, Search } from '@element-plus/icons-vue'

const activities = ref([
  {
    content: '系统初始化完成',
    timestamp: '2024-02-08 12:00:00'
  },
  {
    content: '欢迎使用 ANY-GO 系统',
    timestamp: '2024-02-08 12:00:00'
  }
])

const handleQuickAction = (type: string) => {
  switch (type) {
    case 'product':
      // 跳转到新增产品页面
      break
    case 'packing':
      // 跳转到创建装箱单页面
      break
    case 'search':
      // 跳转到库存查询页面
      break
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.box-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  padding: 20px 0;
}

.el-button {
  width: 100%;
  margin-bottom: 10px;
}
</style>