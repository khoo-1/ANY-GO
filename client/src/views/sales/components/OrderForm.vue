<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
  >
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="店铺名称" prop="storeName">
          <el-input v-model="form.storeName" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="平台" prop="platform">
          <el-select v-model="form.platform" style="width: 100%">
            <el-option label="Amazon" value="amazon" />
            <el-option label="eBay" value="ebay" />
            <el-option label="Shopify" value="shopify" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="订单日期" prop="orderDate">
          <el-date-picker
            v-model="form.orderDate"
            type="date"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="客户姓名" prop="customerName">
          <el-input v-model="form.customerName" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="客户邮箱" prop="customerEmail">
          <el-input v-model="form.customerEmail" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="订单状态" prop="status">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider>收货地址</el-divider>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="国家/地区" prop="shippingAddress.country">
          <el-input v-model="form.shippingAddress.country" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="州/省" prop="shippingAddress.state">
          <el-input v-model="form.shippingAddress.state" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="城市" prop="shippingAddress.city">
          <el-input v-model="form.shippingAddress.city" />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="16">
        <el-form-item label="详细地址" prop="shippingAddress.address">
          <el-input v-model="form.shippingAddress.address" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="邮编" prop="shippingAddress.zipCode">
          <el-input v-model="form.shippingAddress.zipCode" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider>订单明细</el-divider>
    <el-table :data="form.items" border style="width: 100%">
      <el-table-column type="index" width="50" />
      <el-table-column label="商品" min-width="300">
        <template #default="{ row }">
          <el-select
            v-model="row.productId"
            filterable
            remote
            :remote-method="searchProducts"
            :loading="productLoading"
            style="width: 100%"
            @change="handleProductChange($event, row)"
          >
            <el-option
              v-for="item in productOptions"
              :key="item.id"
              :label="`${item.sku} - ${item.name}`"
              :value="item.id"
            />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="数量" width="150">
        <template #default="{ row }">
          <el-input-number
            v-model="row.quantity"
            :min="1"
            @change="calculateItemTotal(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="单价" width="150">
        <template #default="{ row }">
          <el-input-number
            v-model="row.unitPrice"
            :precision="2"
            :step="0.01"
            @change="calculateItemTotal(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="税费" width="150">
        <template #default="{ row }">
          <el-input-number
            v-model="row.tax"
            :precision="2"
            :step="0.01"
            @change="calculateItemTotal(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="折扣" width="150">
        <template #default="{ row }">
          <el-input-number
            v-model="row.discount"
            :precision="2"
            :step="0.01"
            @change="calculateItemTotal(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="小计" width="150">
        <template #default="{ row }">
          {{ formatCurrency(row.total) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ $index }">
          <el-button
            link
            type="danger"
            @click="removeItem($index)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="table-footer">
      <el-button type="primary" @click="addItem">添加商品</el-button>
    </div>

    <el-divider>费用信息</el-divider>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="运费" prop="shippingFee">
          <el-input-number
            v-model="form.shippingFee"
            :precision="2"
            :step="0.01"
            style="width: 100%"
            @change="calculateTotal"
          />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="订单折扣" prop="discount">
          <el-input-number
            v-model="form.discount"
            :precision="2"
            :step="0.01"
            style="width: 100%"
            @change="calculateTotal"
          />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="订单总额">
          <el-input
            v-model="form.total"
            disabled
            style="width: 100%"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider>物流信息</el-divider>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="承运商" prop="carrier">
          <el-input v-model="form.carrier" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="物流单号" prop="trackingNo">
          <el-input v-model="form.trackingNo" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="发货日期" prop="shippingDate">
          <el-date-picker
            v-model="form.shippingDate"
            type="date"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="备注" prop="notes">
      <el-input
        v-model="form.notes"
        type="textarea"
        :rows="3"
      />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit">保存</el-button>
      <el-button @click="$emit('cancel')">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import type { Order, OrderItem } from '@/types/sales'
import type { Product } from '@/types/product'
import productApi from '@/api/product'
import { formatCurrency } from '@/utils/format'

const props = defineProps<{
  type: 'add' | 'edit'
  data?: Order | null
}>()

const emit = defineEmits<{
  (e: 'submit', data: any): void
  (e: 'cancel'): void
}>()

// 表单实例
const formRef = ref<FormInstance>()

// 表单数据
const form = reactive<{
  storeName: string
  platform: string
  orderDate: string
  customerName: string
  customerEmail: string
  status: string
  shippingAddress: {
    country: string
    state: string
    city: string
    address: string
    zipCode: string
  }
  items: OrderItem[]
  shippingFee: number
  discount: number
  total: number
  carrier: string
  trackingNo: string
  shippingDate: string
  notes: string
}>({
  storeName: '',
  platform: '',
  orderDate: '',
  customerName: '',
  customerEmail: '',
  status: 'pending',
  shippingAddress: {
    country: '',
    state: '',
    city: '',
    address: '',
    zipCode: ''
  },
  items: [],
  shippingFee: 0,
  discount: 0,
  total: 0,
  carrier: '',
  trackingNo: '',
  shippingDate: '',
  notes: ''
})

// 表单校验规则
const rules = {
  storeName: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  orderDate: [{ required: true, message: '请选择订单日期', trigger: 'change' }],
  status: [{ required: true, message: '请选择订单状态', trigger: 'change' }]
}

// 商品选择
const productLoading = ref(false)
const productOptions = ref<Product[]>([])

const searchProducts = async (query: string) => {
  if (!query) return
  productLoading.value = true
  try {
    const res = await productApi.list({ keyword: query, pageSize: 20 })
    productOptions.value = res.items
  } finally {
    productLoading.value = false
  }
}

const handleProductChange = async (productId: number, item: OrderItem) => {
  const product = productOptions.value.find(p => p.id === productId)
  if (product) {
    item.sku = product.sku
    item.productName = product.name
    item.unitPrice = product.price
    calculateItemTotal(item)
  }
}

// 订单明细操作
const addItem = () => {
  form.items.push({
    productId: 0,
    sku: '',
    productName: '',
    quantity: 1,
    unitPrice: 0,
    tax: 0,
    discount: 0,
    subtotal: 0,
    total: 0
  })
}

const removeItem = (index: number) => {
  form.items.splice(index, 1)
  calculateTotal()
}

const calculateItemTotal = (item: OrderItem) => {
  item.subtotal = item.quantity * item.unitPrice
  item.total = item.subtotal + item.tax - item.discount
  calculateTotal()
}

const calculateTotal = () => {
  const itemsTotal = form.items.reduce((sum, item) => sum + item.total, 0)
  form.total = itemsTotal + form.shippingFee - form.discount
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  emit('submit', form)
}

// 初始化表单数据
if (props.data) {
  Object.assign(form, props.data)
}
</script>

<style scoped>
.table-footer {
  margin: 16px 0;
  display: flex;
  justify-content: center;
}
</style> 