<template>
  <div class="packing-edit-container">
    <el-card class="edit-card">
      <template #header>
        <div class="card-header">
          <h3>{{ isEdit ? '编辑装箱单' : '新建装箱单' }}</h3>
          <div class="header-actions">
            <el-button @click="handleCancel">
              取消
            </el-button>
            <el-button type="primary" @click="handleSubmit" :loading="loading">
              保存
            </el-button>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="店铺名称" prop="storeName">
              <el-input v-model="formData.storeName" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="类型" prop="type">
              <el-select v-model="formData.type" placeholder="请选择">
                <el-option label="普货" value="普货" />
                <el-option label="纺织" value="纺织" />
                <el-option label="混装" value="混装" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备注" prop="remarks">
              <el-input v-model="formData.remarks" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 商品明细 -->
        <div class="section">
          <div class="section-header">
            <h4>商品明细</h4>
            <el-button type="primary" @click="handleAddItem">
              <el-icon><Plus /></el-icon>
              添加商品
            </el-button>
          </div>

          <el-table :data="formData.items" border>
            <el-table-column label="商品" min-width="300">
              <template #default="{ row, $index }">
                <el-form-item
                  :prop="'items.' + $index + '.productId'"
                  :rules="{ required: true, message: '请选择商品', trigger: 'change' }"
                >
                  <el-select
                    v-model="row.productId"
                    filterable
                    remote
                    :remote-method="handleSearchProducts"
                    :loading="productsLoading"
                    @change="(val) => handleProductChange(val, $index)"
                  >
                    <el-option
                      v-for="item in productOptions"
                      :key="item.id"
                      :label="item.name"
                      :value="item.id"
                    >
                      <div>{{ item.name }}</div>
                      <div class="text-gray">
                        {{ item.sku }} | {{ item.chineseName }}
                      </div>
                    </el-option>
                  </el-select>
                </el-form-item>
              </template>
            </el-table-column>
            <el-table-column label="总数量" width="150">
              <template #default="{ row, $index }">
                <el-form-item
                  :prop="'items.' + $index + '.quantity'"
                  :rules="{ required: true, type: 'number', min: 1, message: '请输入有效数量', trigger: 'blur' }"
                >
                  <el-input-number
                    v-model="row.quantity"
                    :min="1"
                    controls-position="right"
                  />
                </el-form-item>
              </template>
            </el-table-column>
            <el-table-column label="装箱明细" min-width="300">
              <template #default="{ row, $index }">
                <div
                  v-for="(box, boxIndex) in row.boxQuantities"
                  :key="boxIndex"
                  class="box-quantity-item"
                >
                  <el-input
                    v-model="box.boxNo"
                    placeholder="箱号"
                    style="width: 100px"
                  />
                  <el-input-number
                    v-model="box.quantity"
                    :min="1"
                    controls-position="right"
                    placeholder="数量"
                  />
                  <el-input
                    v-model="box.specs"
                    placeholder="规格说明"
                    style="width: 150px"
                  />
                  <el-button
                    type="danger"
                    link
                    @click="handleRemoveBox($index, boxIndex)"
                  >
                    删除
                  </el-button>
                </div>
                <el-button
                  type="primary"
                  link
                  @click="handleAddBox($index)"
                >
                  添加箱子
                </el-button>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  link
                  @click="handleRemoveItem($index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 箱子规格 -->
        <div class="section">
          <div class="section-header">
            <h4>箱子规格</h4>
            <el-button type="primary" @click="handleAddBoxSpec">
              <el-icon><Plus /></el-icon>
              添加规格
            </el-button>
          </div>

          <el-table :data="formData.boxSpecs" border>
            <el-table-column label="长(cm)" width="150">
              <template #default="{ row, $index }">
                <el-form-item
                  :prop="'boxSpecs.' + $index + '.length'"
                  :rules="{ required: true, type: 'number', min: 0, message: '请输入有效长度', trigger: 'blur' }"
                >
                  <el-input-number
                    v-model="row.length"
                    :min="0"
                    :precision="2"
                    controls-position="right"
                  />
                </el-form-item>
              </template>
            </el-table-column>
            <el-table-column label="宽(cm)" width="150">
              <template #default="{ row, $index }">
                <el-form-item
                  :prop="'boxSpecs.' + $index + '.width'"
                  :rules="{ required: true, type: 'number', min: 0, message: '请输入有效宽度', trigger: 'blur' }"
                >
                  <el-input-number
                    v-model="row.width"
                    :min="0"
                    :precision="2"
                    controls-position="right"
                  />
                </el-form-item>
              </template>
            </el-table-column>
            <el-table-column label="高(cm)" width="150">
              <template #default="{ row, $index }">
                <el-form-item
                  :prop="'boxSpecs.' + $index + '.height'"
                  :rules="{ required: true, type: 'number', min: 0, message: '请输入有效高度', trigger: 'blur' }"
                >
                  <el-input-number
                    v-model="row.height"
                    :min="0"
                    :precision="2"
                    controls-position="right"
                  />
                </el-form-item>
              </template>
            </el-table-column>
            <el-table-column label="重量(kg)" width="150">
              <template #default="{ row, $index }">
                <el-form-item
                  :prop="'boxSpecs.' + $index + '.weight'"
                  :rules="{ required: true, type: 'number', min: 0, message: '请输入有效重量', trigger: 'blur' }"
                >
                  <el-input-number
                    v-model="row.weight"
                    :min="0"
                    :precision="2"
                    controls-position="right"
                  />
                </el-form-item>
              </template>
            </el-table-column>
            <el-table-column label="总件数" width="150">
              <template #default="{ row, $index }">
                <el-form-item
                  :prop="'boxSpecs.' + $index + '.totalPieces'"
                  :rules="{ required: true, type: 'number', min: 1, message: '请输入有效件数', trigger: 'blur' }"
                >
                  <el-input-number
                    v-model="row.totalPieces"
                    :min="1"
                    controls-position="right"
                  />
                </el-form-item>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  link
                  @click="handleRemoveBoxSpec($index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import * as packingApi from '../../api/packing'
import * as productApi from '../../api/product'
import type {
  PackingList,
  PackingListItem,
  BoxSpecs,
  BoxQuantity,
  Product
} from '../../types/packing'

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const productsLoading = ref(false)
const productOptions = ref<Product[]>([])

const isEdit = computed(() => route.params.id !== undefined)

// 表单数据
const formData = reactive<{
  storeName: string
  type: string
  remarks?: string
  items: Partial<PackingListItem>[]
  boxSpecs: Partial<BoxSpecs>[]
}>({
  storeName: '',
  type: '',
  remarks: '',
  items: [],
  boxSpecs: []
})

// 表单验证规则
const rules = {
  storeName: [
    { required: true, message: '请输入店铺名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择类型', trigger: 'change' }
  ],
  'items.*.productId': [
    { required: true, message: '请选择商品', trigger: 'change' }
  ],
  'items.*.quantity': [
    { required: true, message: '请输入数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '数量必须大于0', trigger: 'blur' }
  ],
  'items.*.boxQuantities': [
    { required: true, message: '请添加装箱明细', trigger: 'change' },
    { 
      validator: (rule: any, value: BoxQuantity[]) => {
        if (!value || !value.length) {
          return Promise.reject('请添加装箱明细')
        }
        // 验证总数量是否匹配
        const index = parseInt(rule.field.split('.')[1])
        const item = formData.items[index]
        const totalBoxQuantity = value.reduce((sum, box) => sum + box.quantity, 0)
        if (totalBoxQuantity !== item.quantity) {
          return Promise.reject('装箱数量总和必须等于商品总数量')
        }
        return Promise.resolve()
      },
      trigger: 'change'
    }
  ],
  'boxSpecs.*.length': [
    { required: true, message: '请输入长度', trigger: 'blur' },
    { type: 'number', min: 0, message: '长度必须大于0', trigger: 'blur' }
  ],
  'boxSpecs.*.width': [
    { required: true, message: '请输入宽度', trigger: 'blur' },
    { type: 'number', min: 0, message: '宽度必须大于0', trigger: 'blur' }
  ],
  'boxSpecs.*.height': [
    { required: true, message: '请输入高度', trigger: 'blur' },
    { type: 'number', min: 0, message: '高度必须大于0', trigger: 'blur' }
  ],
  'boxSpecs.*.weight': [
    { required: true, message: '请输入重量', trigger: 'blur' },
    { type: 'number', min: 0, message: '重量必须大于0', trigger: 'blur' }
  ]
}

// 加载编辑数据
const loadEditData = async () => {
  try {
    loading.value = true
    const id = parseInt(route.params.id as string)
    const res = await packingApi.getPackingList(id)
    formData.storeName = res.storeName
    formData.type = res.type
    formData.remarks = res.remarks
    formData.items = res.items.map(item => ({
      productId: item.product.id,
      product: item.product,
      quantity: item.quantity,
      boxQuantities: item.boxQuantities
    }))
    formData.boxSpecs = res.boxSpecs
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索商品
const handleSearchProducts = async (query: string) => {
  if (!query) return
  try {
    productsLoading.value = true
    const res = await productApi.searchProducts({ keyword: query })
    productOptions.value = res.items
  } catch (error) {
    console.error('搜索商品失败:', error)
    ElMessage.error('搜索商品失败')
  } finally {
    productsLoading.value = false
  }
}

// 商品选择变更
const handleProductChange = (productId: number, index: number) => {
  const product = productOptions.value.find(item => item.id === productId)
  if (product) {
    formData.items[index].product = product
  }
}

// 添加商品
const handleAddItem = () => {
  formData.items.push({
    productId: undefined,
    quantity: 1,
    boxQuantities: []
  })
}

// 删除商品
const handleRemoveItem = (index: number) => {
  formData.items.splice(index, 1)
}

// 添加箱子
const handleAddBox = (itemIndex: number) => {
  if (!formData.items[itemIndex].boxQuantities) {
    formData.items[itemIndex].boxQuantities = []
  }
  formData.items[itemIndex].boxQuantities?.push({
    boxNo: '',
    quantity: 1
  })
}

// 删除箱子
const handleRemoveBox = (itemIndex: number, boxIndex: number) => {
  formData.items[itemIndex].boxQuantities?.splice(boxIndex, 1)
}

// 添加箱子规格
const handleAddBoxSpec = () => {
  formData.boxSpecs.push({
    length: 0,
    width: 0,
    height: 0,
    weight: 0,
    volume: 0,
    edgeVolume: 0,
    totalPieces: 1
  })
}

// 删除箱子规格
const handleRemoveBoxSpec = (index: number) => {
  formData.boxSpecs.splice(index, 1)
}

// 取消
const handleCancel = () => {
  router.back()
}

// 提交前的额外验证
const validateBeforeSubmit = () => {
  // 验证是否有商品
  if (!formData.items.length) {
    ElMessage.error('请至少添加一个商品')
    return false
  }

  // 验证是否有箱子规格
  if (!formData.boxSpecs.length) {
    ElMessage.error('请至少添加一个箱子规格')
    return false
  }

  // 验证每个商品的装箱明细
  for (const item of formData.items) {
    if (!item.boxQuantities?.length) {
      ElMessage.error(`商品 ${item.product?.sku} 缺少装箱明细`)
      return false
    }

    const totalBoxQuantity = item.boxQuantities.reduce((sum, box) => sum + box.quantity, 0)
    if (totalBoxQuantity !== item.quantity) {
      ElMessage.error(`商品 ${item.product?.sku} 的装箱数量总和(${totalBoxQuantity})与商品总数量(${item.quantity})不匹配`)
      return false
    }
  }

  return true
}

// 更新提交方法
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    // 表单验证
    await formRef.value.validate()
    
    // 额外验证
    if (!validateBeforeSubmit()) {
      return
    }

    loading.value = true
    
    // 准备提交数据
    const submitData = {
      storeName: formData.storeName,
      type: formData.type,
      remarks: formData.remarks,
      items: formData.items.map(item => ({
        productId: item.productId,
        quantity: item.quantity,
        boxQuantities: item.boxQuantities
      })),
      boxSpecs: formData.boxSpecs
    }

    if (isEdit.value) {
      await packingApi.updatePackingList(parseInt(route.params.id as string), submitData)
      ElMessage.success('更新成功')
    } else {
      await packingApi.createPackingList(submitData)
      ElMessage.success('创建成功')
    }
    
    router.push('/packing-lists')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    loading.value = false
  }
}

// 初始加载
onMounted(() => {
  if (isEdit.value) {
    loadEditData()
  }
})
</script>

<style scoped>
.packing-edit-container {
  padding: 20px;
}

.edit-card {
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.text-gray {
  color: #666;
  font-size: 0.9em;
}

.box-quantity-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}
</style> 