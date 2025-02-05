<template>
  <div class="packing-print-container" ref="printRef">
    <div class="print-header">
      <h1>装箱单</h1>
      <div class="print-info">
        <div>单号: {{ packingList?.code }}</div>
        <div>日期: {{ formatDate(packingList?.createdAt) }}</div>
      </div>
    </div>

    <div class="print-content">
      <div class="basic-info">
        <div class="info-item">
          <span class="label">店铺名称:</span>
          <span>{{ packingList?.storeName }}</span>
        </div>
        <div class="info-item">
          <span class="label">类型:</span>
          <span>{{ packingList?.type }}</span>
        </div>
        <div class="info-item">
          <span class="label">总箱数:</span>
          <span>{{ packingList?.totalBoxes }}</span>
        </div>
        <div class="info-item">
          <span class="label">总件数:</span>
          <span>{{ packingList?.totalPieces }}</span>
        </div>
        <div class="info-item">
          <span class="label">总重量:</span>
          <span>{{ packingList?.totalWeight }} kg</span>
        </div>
        <div class="info-item">
          <span class="label">总体积:</span>
          <span>{{ packingList?.totalVolume }} m³</span>
        </div>
      </div>

      <div class="section">
        <h3>商品明细</h3>
        <table class="print-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>商品名称</th>
              <th>类型</th>
              <th>数量</th>
              <th>装箱明细</th>
              <th>重量(kg)</th>
              <th>体积(m³)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in packingList?.items" :key="item.product.id">
              <td>{{ item.product.sku }}</td>
              <td>
                <div>{{ item.product.name }}</div>
                <div class="text-gray">{{ item.product.chineseName }}</div>
              </td>
              <td>{{ item.product.type }}</td>
              <td>{{ item.quantity }}</td>
              <td>
                <div v-for="box in item.boxQuantities" :key="box.boxNo">
                  {{ box.boxNo }}: {{ box.quantity }}件
                  <template v-if="box.specs">
                    ({{ box.specs }})
                  </template>
                </div>
              </td>
              <td>{{ item.weight }}</td>
              <td>{{ item.volume }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section">
        <h3>箱子规格</h3>
        <table class="print-table">
          <thead>
            <tr>
              <th>箱号</th>
              <th>长(cm)</th>
              <th>宽(cm)</th>
              <th>高(cm)</th>
              <th>重量(kg)</th>
              <th>体积(m³)</th>
              <th>棱边体积(m³)</th>
              <th>总件数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(spec, index) in packingList?.boxSpecs" :key="index">
              <td>{{ index + 1 }}</td>
              <td>{{ spec.length }}</td>
              <td>{{ spec.width }}</td>
              <td>{{ spec.height }}</td>
              <td>{{ spec.weight }}</td>
              <td>{{ spec.volume }}</td>
              <td>{{ spec.edgeVolume }}</td>
              <td>{{ spec.totalPieces }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="signatures">
        <div class="signature-item">
          <div class="signature-line">制单人: _____________</div>
          <div class="signature-date">日期: _____________</div>
        </div>
        <div class="signature-item">
          <div class="signature-line">审核人: _____________</div>
          <div class="signature-date">日期: _____________</div>
        </div>
        <div class="signature-item">
          <div class="signature-line">收货人: _____________</div>
          <div class="signature-date">日期: _____________</div>
        </div>
      </div>
    </div>
  </div>

  <div class="print-actions" v-if="!isPrinting">
    <el-button type="primary" @click="handlePrint">
      <el-icon><Printer /></el-icon>
      打印
    </el-button>
    <el-button @click="handleBack">
      返回
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as packingApi from '../../api/packing'
import type { PackingList } from '../../types/packing'

const route = useRoute()
const router = useRouter()
const printRef = ref<HTMLElement>()
const isPrinting = ref(false)
const packingList = ref<PackingList | null>(null)

// 格式化日期
const formatDate = (date?: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

// 加载数据
const loadData = async () => {
  try {
    const id = parseInt(route.params.id as string)
    const res = await packingApi.getPackingList(id)
    packingList.value = res
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

// 打印处理
const handlePrint = () => {
  isPrinting.value = true
  window.print()
}

// 返回
const handleBack = () => {
  router.back()
}

// 监听打印事件
const handleAfterPrint = () => {
  isPrinting.value = false
}

onMounted(() => {
  loadData()
  window.addEventListener('afterprint', handleAfterPrint)
})

onBeforeUnmount(() => {
  window.removeEventListener('afterprint', handleAfterPrint)
})
</script>

<style scoped>
/* 打印样式 */
@media print {
  .print-actions {
    display: none;
  }

  .packing-print-container {
    padding: 20px;
  }
}

/* 常规样式 */
.packing-print-container {
  padding: 20px;
  background: white;
}

.print-header {
  text-align: center;
  margin-bottom: 20px;
}

.print-info {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
}

.basic-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  gap: 10px;
}

.label {
  font-weight: bold;
}

.section {
  margin: 20px 0;
}

.print-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

.print-table th,
.print-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.print-table th {
  background-color: #f5f7fa;
}

.text-gray {
  color: #666;
  font-size: 0.9em;
}

.signatures {
  display: flex;
  justify-content: space-between;
  margin-top: 50px;
}

.signature-item {
  text-align: center;
}

.signature-line {
  margin-bottom: 10px;
}

.print-actions {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
  z-index: 100;
}
</style> 