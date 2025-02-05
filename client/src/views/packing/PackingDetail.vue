<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>装箱单详情</h2>
      </div>
      <div class="header-actions">
        <el-button @click="handlePrint">打印</el-button>
        <el-button 
          v-if="packingList?.status === 'pending'"
          type="success" 
          @click="handleApprove"
        >
          审核通过
        </el-button>
        <el-button 
          v-if="packingList?.status === 'pending'"
          type="primary" 
          @click="handleEdit"
        >
          编辑
        </el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <!-- 基本信息 -->
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-tag :type="packingList?.status === 'approved' ? 'success' : ''">
            {{ packingList?.status === 'approved' ? '已审核' : '待审核' }}
          </el-tag>
        </div>
      </template>
      
      <el-descriptions :column="3" border>
        <el-descriptions-item label="店铺名称">
          {{ packingList?.storeName }}
        </el-descriptions-item>
        <el-descriptions-item label="类型">
          {{ packingList?.type }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ packingList?.createdAt ? new Date(packingList.createdAt).toLocaleString() : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="总箱数">
          {{ packingList?.totalBoxes }}
        </el-descriptions-item>
        <el-descriptions-item label="总件数">
          {{ packingList?.totalPieces }}
        </el-descriptions-item>
        <el-descriptions-item label="总价值">
          ¥{{ packingList?.totalValue?.toFixed(2) }}
        </el-descriptions-item>
        <el-descriptions-item label="总重量">
          {{ packingList?.totalWeight?.toFixed(2) }}kg
        </el-descriptions-item>
        <el-descriptions-item label="总体积">
          {{ packingList?.totalVolume?.toFixed(2) }}m³
        </el-descriptions-item>
        <el-descriptions-item label="备注">
          {{ packingList?.remarks || '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 商品明细 -->
      <div class="section">
        <h3>商品明细</h3>
        <el-table :data="packingList?.items || []" border>
          <el-table-column prop="product.sku" label="SKU" width="150" />
          <el-table-column prop="product.name" label="商品名称" min-width="200" />
          <el-table-column prop="product.chineseName" label="中文名称" min-width="200" />
          <el-table-column prop="quantity" label="总数量" width="100" />
          <el-table-column label="装箱明细" width="200">
            <template #default="{ row }">
              <div v-for="(box, index) in row.boxQuantities" :key="index">
                {{ box.boxNo }}: {{ box.quantity }}件
              </div>
            </template>
          </el-table-column>
          <el-table-column label="重量/体积" width="150">
            <template #default="{ row }">
              {{ row.weight?.toFixed(2) }}kg / {{ row.volume?.toFixed(2) }}m³
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 箱子规格 -->
      <div class="section">
        <h3>箱子规格</h3>
        <el-table :data="packingList?.boxSpecs || []" border>
          <el-table-column type="index" label="箱号" width="80" />
          <el-table-column label="尺寸(cm)" width="200">
            <template #default="{ row }">
              {{ row.length }} × {{ row.width }} × {{ row.height }}
            </template>
          </el-table-column>
          <el-table-column prop="weight" label="重量(kg)" width="120">
            <template #default="{ row }">
              {{ row.weight?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="体积(m³)" width="120">
            <template #default="{ row }">
              {{ row.volume?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="边体积(m³)" width="120">
            <template #default="{ row }">
              {{ row.edgeVolume?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="totalPieces" label="总件数" width="100" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import type { PackingList } from '@/types/packing'
import packingApi from '@/api/packing'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const packingList = ref<PackingList>()

// 加载数据
async function loadData() {
  const id = Number(route.params.id)
  if (!id) return

  loading.value = true
  try {
    packingList.value = await packingApi.get(id)
  } catch (error) {
    console.error('加载装箱单详情失败:', error)
    ElMessage.error('加载装箱单详情失败')
  } finally {
    loading.value = false
  }
}

// 审核通过
async function handleApprove() {
  try {
    await ElMessageBox.confirm('确定要审核通过该装箱单吗？')
    await packingApi.approve(packingList.value!.id!)
    ElMessage.success('审核成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核失败:', error)
      ElMessage.error('审核失败')
    }
  }
}

// 编辑
function handleEdit() {
  router.push(`/packing-lists/${packingList.value?.id}/edit`)
}

// 打印
function handlePrint() {
  router.push(`/packing-lists/${packingList.value?.id}/print`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section {
  margin-top: 24px;
}

.section h3 {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 500;
}
</style> 