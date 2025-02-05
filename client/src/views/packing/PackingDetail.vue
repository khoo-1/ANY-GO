<template>
  <div class="packing-detail-container">
    <el-card class="detail-card">
      <template #header>
        <div class="card-header">
          <h3>装箱单详情</h3>
          <div class="header-actions">
            <el-button
              type="primary"
              @click="handleEdit"
              v-if="packingList?.status === 'pending'"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              type="success"
              @click="handleApprove"
              v-if="packingList?.status === 'pending'"
            >
              <el-icon><Check /></el-icon>
              通过
            </el-button>
            <el-button
              type="danger"
              @click="handleReject"
              v-if="packingList?.status === 'pending'"
            >
              <el-icon><Close /></el-icon>
              拒绝
            </el-button>
            <el-button @click="handlePrint">
              <el-icon><Printer /></el-icon>
              打印
            </el-button>
          </div>
        </div>
      </template>

      <el-descriptions
        v-loading="loading"
        :column="3"
        border
      >
        <el-descriptions-item label="装箱单号">
          {{ packingList?.code }}
        </el-descriptions-item>
        <el-descriptions-item label="店铺名称">
          {{ packingList?.storeName }}
        </el-descriptions-item>
        <el-descriptions-item label="类型">
          {{ packingList?.type }}
        </el-descriptions-item>
        <el-descriptions-item label="总箱数">
          {{ packingList?.totalBoxes }}
        </el-descriptions-item>
        <el-descriptions-item label="总件数">
          {{ packingList?.totalPieces }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(packingList?.status)">
            {{ getStatusText(packingList?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总重量">
          {{ packingList?.totalWeight }} kg
        </el-descriptions-item>
        <el-descriptions-item label="总体积">
          {{ packingList?.totalVolume }} m³
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ packingList?.createdAt }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="3">
          {{ packingList?.remarks || '无' }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 商品明细 -->
      <div class="section">
        <h4>商品明细</h4>
        <el-table :data="packingList?.items || []" border>
          <el-table-column prop="product.sku" label="SKU" width="120" />
          <el-table-column prop="product.name" label="商品名称" min-width="200">
            <template #default="{ row }">
              <div>{{ row.product.name }}</div>
              <div class="text-gray">{{ row.product.chineseName }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="product.type" label="类型" width="100" />
          <el-table-column prop="quantity" label="总数量" width="100" />
          <el-table-column label="装箱明细" min-width="200">
            <template #default="{ row }">
              <el-tag
                v-for="box in row.boxQuantities"
                :key="box.boxNo"
                class="box-tag"
              >
                {{ box.boxNo }}: {{ box.quantity }}件
                <template v-if="box.specs">
                  ({{ box.specs }})
                </template>
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="weight" label="重量(kg)" width="100" />
          <el-table-column prop="volume" label="体积(m³)" width="100" />
        </el-table>
      </div>

      <!-- 箱子规格 -->
      <div class="section">
        <h4>箱子规格</h4>
        <el-table :data="packingList?.boxSpecs || []" border>
          <el-table-column type="index" label="箱号" width="80" />
          <el-table-column prop="length" label="长(cm)" width="100" />
          <el-table-column prop="width" label="宽(cm)" width="100" />
          <el-table-column prop="height" label="高(cm)" width="100" />
          <el-table-column prop="weight" label="重量(kg)" width="100" />
          <el-table-column prop="volume" label="体积(m³)" width="100" />
          <el-table-column prop="edgeVolume" label="棱边体积(m³)" width="120" />
          <el-table-column prop="totalPieces" label="总件数" width="100" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as packingApi from '../../api/packing'
import type { PackingList } from '../../types/packing'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const packingList = ref<PackingList | null>(null)

// 获取装箱单详情
const loadData = async () => {
  try {
    loading.value = true
    const id = parseInt(route.params.id as string)
    const res = await packingApi.getPackingList(id)
    packingList.value = res
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 状态相关方法
const getStatusType = (status?: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return map[status || ''] || 'info'
}

const getStatusText = (status?: string) => {
  const map: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status || ''] || status || ''
}

// 操作方法
const handleEdit = () => {
  router.push(`/packing-lists/${route.params.id}/edit`)
}

const handlePrint = () => {
  router.push(`/packing-lists/${route.params.id}/print`)
}

const handleApprove = async () => {
  try {
    await ElMessageBox.confirm('确定要通过该装箱单吗？')
    await packingApi.approvePackingLists([parseInt(route.params.id as string)])
    ElMessage.success('操作成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审批失败:', error)
      ElMessage.error('审批失败')
    }
  }
}

const handleReject = async () => {
  try {
    await ElMessageBox.confirm('确定要拒绝该装箱单吗？')
    await packingApi.rejectPackingLists([parseInt(route.params.id as string)])
    ElMessage.success('操作成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('拒绝失败:', error)
      ElMessage.error('拒绝失败')
    }
  }
}

// 初始加载
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.packing-detail-container {
  padding: 20px;
}

.detail-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.section {
  margin-top: 20px;
}

.text-gray {
  color: #666;
  font-size: 0.9em;
}

.box-tag {
  margin: 2px;
}
</style> 