<template>
  <div class="order-detail">
    <el-descriptions title="基本信息" :column="3" border>
      <el-descriptions-item label="订单号">{{ data.orderNo }}</el-descriptions-item>
      <el-descriptions-item label="店铺名称">{{ data.storeName }}</el-descriptions-item>
      <el-descriptions-item label="平台">{{ data.platform }}</el-descriptions-item>
      <el-descriptions-item label="订单日期">{{ data.orderDate }}</el-descriptions-item>
      <el-descriptions-item label="订单状态">
        <el-tag :type="getOrderStatusType(data.status)">
          {{ getOrderStatusText(data.status) }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="支付状态">
        <el-tag :type="getPaymentStatusType(data.paymentStatus)">
          {{ getPaymentStatusText(data.paymentStatus) }}
        </el-tag>
      </el-descriptions-item>
    </el-descriptions>

    <el-descriptions title="客户信息" :column="2" border>
      <el-descriptions-item label="客户姓名">{{ data.customerName }}</el-descriptions-item>
      <el-descriptions-item label="客户邮箱">{{ data.customerEmail }}</el-descriptions-item>
      <el-descriptions-item label="收货地址" :span="2">
        {{ formatAddress(data.shippingAddress) }}
      </el-descriptions-item>
    </el-descriptions>

    <el-descriptions title="物流信息" :column="3" border>
      <el-descriptions-item label="承运商">{{ data.carrier }}</el-descriptions-item>
      <el-descriptions-item label="物流单号">{{ data.trackingNo }}</el-descriptions-item>
      <el-descriptions-item label="发货日期">{{ data.shippingDate }}</el-descriptions-item>
    </el-descriptions>

    <div class="section-title">订单明细</div>
    <el-table :data="data.items" border style="width: 100%">
      <el-table-column type="index" width="50" />
      <el-table-column prop="sku" label="SKU" width="150" />
      <el-table-column prop="productName" label="商品名称" min-width="200" />
      <el-table-column prop="quantity" label="数量" width="100" />
      <el-table-column prop="unitPrice" label="单价" width="120">
        <template #default="{ row }">
          {{ formatCurrency(row.unitPrice) }}
        </template>
      </el-table-column>
      <el-table-column prop="tax" label="税费" width="120">
        <template #default="{ row }">
          {{ formatCurrency(row.tax) }}
        </template>
      </el-table-column>
      <el-table-column prop="discount" label="折扣" width="120">
        <template #default="{ row }">
          {{ formatCurrency(row.discount) }}
        </template>
      </el-table-column>
      <el-table-column prop="total" label="小计" width="120">
        <template #default="{ row }">
          {{ formatCurrency(row.total) }}
        </template>
      </el-table-column>
    </el-table>

    <div class="amount-summary">
      <div class="amount-item">
        <span class="label">商品总额：</span>
        <span class="value">{{ formatCurrency(getSubtotal()) }}</span>
      </div>
      <div class="amount-item">
        <span class="label">运费：</span>
        <span class="value">{{ formatCurrency(data.shippingFee) }}</span>
      </div>
      <div class="amount-item">
        <span class="label">订单折扣：</span>
        <span class="value">{{ formatCurrency(data.discount) }}</span>
      </div>
      <div class="amount-item total">
        <span class="label">订单总额：</span>
        <span class="value">{{ formatCurrency(data.total) }}</span>
      </div>
    </div>

    <el-descriptions title="其他信息" :column="2" border>
      <el-descriptions-item label="操作人">{{ data.operatorName }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ data.createdAt }}</el-descriptions-item>
      <el-descriptions-item label="备注" :span="2">{{ data.notes || '-' }}</el-descriptions-item>
    </el-descriptions>

    <div class="actions">
      <el-button @click="$emit('close')">关闭</el-button>
      <el-button type="primary" @click="handlePrint">打印</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Order } from '@/types/sales'
import { formatCurrency } from '@/utils/format'

const props = defineProps<{
  data: Order
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

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

// 格式化地址
const formatAddress = (address: any) => {
  if (!address) return '-'
  const parts = [
    address.country,
    address.state,
    address.city,
    address.address,
    address.zipCode
  ]
  return parts.filter(Boolean).join(', ')
}

// 计算商品总额
const getSubtotal = () => {
  return props.data.items.reduce((sum, item) => sum + item.subtotal, 0)
}

// 打印订单
const handlePrint = () => {
  window.print()
}
</script>

<style scoped>
.order-detail {
  padding: 20px;
}

.section-title {
  margin: 20px 0;
  font-size: 16px;
  font-weight: bold;
}

.amount-summary {
  margin: 20px 0;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.amount-item {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.amount-item:last-child {
  margin-bottom: 0;
}

.amount-item .label {
  margin-right: 20px;
  color: #606266;
}

.amount-item .value {
  min-width: 120px;
  text-align: right;
}

.amount-item.total {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
  font-weight: bold;
}

.actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 20px;
}

@media print {
  .actions {
    display: none;
  }
}
</style> 