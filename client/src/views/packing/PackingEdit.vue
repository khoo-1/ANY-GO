<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>{{ isEdit ? '编辑装箱单' : '新建装箱单' }}</h2>
      </div>
      <div class="header-actions">
        <el-button @click="handleImport">导入</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </div>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      v-loading="loading"
    >
      <!-- 基本信息 -->
      <el-card class="mb-4">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="店铺名称" prop="storeName">
              <el-input v-model="form.storeName" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="类型" prop="type">
              <el-select v-model="form.type" style="width: 100%">
                <el-option label="普货" value="普货" />
                <el-option label="纺织" value="纺织" />
                <el-option label="混装" value="混装" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备注">
              <el-input v-model="form.remarks" type="textarea" :rows="1" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 商品明细 -->
      <el-card class="mb-4">
        <template #header>
          <div class="card-header">
            <span>商品明细</span>
            <el-button type="primary" @click="addItem">添加商品</el-button>
          </div>
        </template>

        <el-table :data="form.items" border>
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
                placeholder="输入SKU或名称搜索"
                @change="handleProductChange($event, row)"
              >
                <el-option
                  v-for="item in productOptions"
                  :key="item.id"
                  :label="`${item.sku} - ${item.name}`"
                  :value="item.id"
                >
                  <div>{{ item.sku }} - {{ item.name }}</div>
                  <div class="text-gray">{{ item.chineseName }}</div>
                </el-option>
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="总数量" width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.quantity"
                :min="1"
                @change="calculateTotals"
              />
            </template>
          </el-table-column>
          <el-table-column label="装箱明细" min-width="300">
            <template #default="{ row }">
              <div
                v-for="(box, index) in row.boxQuantities"
                :key="index"
                class="box-quantity"
              >
                <el-input
                  v-model="box.boxNo"
                  placeholder="箱号"
                  style="width: 100px"
                />
                <el-input-number
                  v-model="box.quantity"
                  :min="1"
                  placeholder="数量"
                  @change="validateBoxQuantities(row)"
                />
                <el-input
                  v-model="box.specs"
                  placeholder="规格说明"
                  style="width: 150px"
                />
                <el-button
                  type="danger"
                  link
                  @click="removeBoxQuantity(row, index)"
                >
                  删除
                </el-button>
              </div>
              <el-button link type="primary" @click="addBoxQuantity(row)">
                添加箱号
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ $index }">
              <el-button
                type="danger"
                link
                @click="removeItem($index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 箱子规格 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>箱子规格</span>
            <el-button type="primary" @click="addBoxSpec">添加箱规</el-button>
          </div>
        </template>

        <el-table :data="form.boxSpecs" border>
          <el-table-column type="index" label="箱号" width="80" />
          <el-table-column label="尺寸(cm)" width="300">
            <template #default="{ row }">
              <el-input-number
                v-model="row.length"
                :min="1"
                placeholder="长"
                @change="calculateBoxVolume(row)"
              />
              ×
              <el-input-number
                v-model="row.width"
                :min="1"
                placeholder="宽"
                @change="calculateBoxVolume(row)"
              />
              ×
              <el-input-number
                v-model="row.height"
                :min="1"
                placeholder="高"
                @change="calculateBoxVolume(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="重量(kg)" width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.weight"
                :min="0"
                :precision="2"
                @change="calculateTotals"
              />
            </template>
          </el-table-column>
          <el-table-column label="体积(m³)" width="120">
            <template #default="{ row }">
              {{ row.volume?.toFixed(4) }}
            </template>
          </el-table-column>
          <el-table-column label="边体积(m³)" width="120">
            <template #default="{ row }">
              {{ row.edgeVolume?.toFixed(4) }}
            </template>
          </el-table-column>
          <el-table-column label="总件数" width="100">
            <template #default="{ row }">
              {{ row.totalPieces }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ $index }">
              <el-button
                type="danger"
                link
                @click="removeBoxSpec($index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="totals">
          <div class="total-item">
            <span class="label">总箱数：</span>
            <span class="value">{{ form.totalBoxes }}</span>
          </div>
          <div class="total-item">
            <span class="label">总重量：</span>
            <span class="value">{{ form.totalWeight?.toFixed(2) }}kg</span>
          </div>
          <div class="total-item">
            <span class="label">总体积：</span>
            <span class="value">{{ form.totalVolume?.toFixed(4) }}m³</span>
          </div>
          <div class="total-item">
            <span class="label">总件数：</span>
            <span class="value">{{ form.totalPieces }}</span>
          </div>
        </div>
      </el-card>
    </el-form>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入装箱单"
      width="500px"
    >
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".xlsx,.xls"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            请上传Excel文件，
            <el-button link type="primary" @click="downloadTemplate">
              下载模板
            </el-button>
          </div>
        </template>
      </el-upload>

      <el-progress
        v-if="importing"
        :percentage="importProgress"
        :status="importProgress === 100 ? 'success' : ''"
      />

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="importing"
            @click="confirmImport"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, UploadFilled } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import type { Product } from '@/types/product'
import type {
  PackingList,
  PackingListItem,
  BoxQuantity,
  BoxSpecs
} from '@/types/packing'
import { usePackingStore } from '@/stores/packing'
import packingApi from '@/api/packing'
import productApi from '@/api/product'
import { generatePackingListTemplate, validatePackingListExcel } from '@/utils/excel'

const router = useRouter()
const route = useRoute()
const packingStore = usePackingStore()

// 表单实例
const formRef = ref<FormInstance>()
const loading = ref(false)
const isEdit = computed(() => !!route.params.id)

// 表单数据
const form = reactive<{
  storeName: string
  type: string
  remarks?: string
  items: PackingListItem[]
  boxSpecs: BoxSpecs[]
  totalBoxes: number
  totalWeight: number
  totalVolume: number
  totalPieces: number
}>({
  storeName: '',
  type: '普货',
  remarks: '',
  items: [],
  boxSpecs: [],
  totalBoxes: 0,
  totalWeight: 0,
  totalVolume: 0,
  totalPieces: 0
})

// 表单验证规则
const rules = {
  storeName: [
    { required: true, message: '请输入店铺名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择类型', trigger: 'change' }
  ]
}

// 商品选择
const productLoading = ref(false)
const productOptions = ref<Product[]>([])

// 导入相关
const importDialogVisible = ref(false)
const importing = ref(false)
const importProgress = ref(0)
const importFile = ref<File>()

// 加载数据
async function loadData() {
  if (!isEdit.value) return
  
  const id = parseInt(route.params.id as string)
  loading.value = true
  try {
    const data = await packingApi.get(id)
    Object.assign(form, data)
  } catch (error) {
    console.error('加载装箱单失败:', error)
    ElMessage.error('加载装箱单失败')
    router.back()
  } finally {
    loading.value = false
  }
}

// 商品搜索
async function searchProducts(query: string) {
  if (!query) return
  
  productLoading.value = true
  try {
    const res = await productApi.list({
      keyword: query,
      pageSize: 20
    })
    productOptions.value = res.items
  } catch (error) {
    console.error('搜索商品失败:', error)
  } finally {
    productLoading.value = false
  }
}

// 商品选择变更
function handleProductChange(productId: number, item: PackingListItem) {
  const product = productOptions.value.find(p => p.id === productId)
  if (product) {
    item.product = product
  }
}

// 商品明细操作
function addItem() {
  form.items.push({
    productId: 0,
    product: {} as Product,
    quantity: 1,
    boxQuantities: [],
    weight: 0,
    volume: 0
  })
}

function removeItem(index: number) {
  form.items.splice(index, 1)
  calculateTotals()
}

function addBoxQuantity(item: PackingListItem) {
  item.boxQuantities.push({
    boxNo: '',
    quantity: 1
  })
}

function removeBoxQuantity(item: PackingListItem, index: number) {
  item.boxQuantities.splice(index, 1)
  validateBoxQuantities(item)
}

// 验证装箱数量
function validateBoxQuantities(item: PackingListItem) {
  const total = item.boxQuantities.reduce((sum, box) => sum + box.quantity, 0)
  if (total !== item.quantity) {
    ElMessage.warning('装箱数量与总数量不符')
  }
  calculateTotals()
}

// 箱规操作
function addBoxSpec() {
  form.boxSpecs.push({
    length: 0,
    width: 0,
    height: 0,
    weight: 0,
    volume: 0,
    edgeVolume: 0,
    totalPieces: 0
  })
}

function removeBoxSpec(index: number) {
  form.boxSpecs.splice(index, 1)
  calculateTotals()
}

// 计算箱子体积
function calculateBoxVolume(box: BoxSpecs) {
  if (box.length && box.width && box.height) {
    // 转换为米
    box.volume = (box.length * box.width * box.height) / 1000000
    // 边加一体积
    box.edgeVolume = ((box.length + 1) * (box.width + 1) * (box.height + 1)) / 1000000
  }
  calculateTotals()
}

// 计算总计
function calculateTotals() {
  // 计算箱子总数
  form.totalBoxes = form.boxSpecs.length

  // 计算总重量
  form.totalWeight = form.boxSpecs.reduce((sum, box) => sum + (box.weight || 0), 0)

  // 计算总体积
  form.totalVolume = form.boxSpecs.reduce((sum, box) => sum + (box.volume || 0), 0)

  // 计算总件数
  form.totalPieces = form.items.reduce((sum, item) => sum + item.quantity, 0)

  // 更新箱子总件数
  const boxQuantities = form.items.flatMap(item => item.boxQuantities)
  form.boxSpecs.forEach(box => {
    box.totalPieces = boxQuantities
      .filter(bq => bq.boxNo === `${form.boxSpecs.indexOf(box) + 1}#`)
      .reduce((sum, bq) => sum + bq.quantity, 0)
  })
}

// 导入相关
function handleImport() {
  importDialogVisible.value = true
  importFile.value = undefined
  importProgress.value = 0
}

function handleFileChange(file: any) {
  importFile.value = file.raw
}

function downloadTemplate() {
  generatePackingListTemplate()
}

async function confirmImport() {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  importing.value = true
  importProgress.value = 30

  try {
    // 验证文件
    const validation = await validatePackingListExcel(importFile.value)
    if (!validation.valid) {
      throw new Error(validation.errors.join('\n'))
    }

    importProgress.value = 60

    // 导入数据
    const formData = new FormData()
    formData.append('file', importFile.value)
    const res = await packingApi.import(formData)

    importProgress.value = 100
    ElMessage.success('导入成功')
    importDialogVisible.value = false

    // 记录导入历史
    packingStore.addImportHistory({
      filename: importFile.value.name,
      success: true
    })

    // 刷新数据
    loadData()
  } catch (error: any) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
    // 记录导入历史
    packingStore.addImportHistory({
      filename: importFile.value.name,
      success: false,
      errors: [error.message]
    })
  } finally {
    importing.value = false
    importProgress.value = 0
  }
}

// 保存
async function handleSave() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    // 验证数据
    if (form.items.length === 0) {
      throw new Error('请添加商品')
    }
    
    if (form.boxSpecs.length === 0) {
      throw new Error('请添加箱规')
    }

    for (const item of form.items) {
      if (!item.productId) {
        throw new Error('请选择商品')
      }
      
      const total = item.boxQuantities.reduce((sum, box) => sum + box.quantity, 0)
      if (total !== item.quantity) {
        throw new Error(`商品 ${item.product.sku} 的装箱数量与总数量不符`)
      }
    }

    loading.value = true
    const startTime = Date.now()

    if (isEdit.value) {
      await packingApi.update(parseInt(route.params.id as string), form)
    } else {
      await packingApi.create(form)
    }

    // 记录性能指标
    packingStore.recordPerformance('saveTime', Date.now() - startTime)

    ElMessage.success('保存成功')
    router.back()
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.mb-4 {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.box-quantity {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}

.totals {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.total-item {
  display: inline-block;
  margin-right: 40px;
}

.total-item:last-child {
  margin-right: 0;
}

.total-item .label {
  margin-right: 8px;
  color: #606266;
}

.total-item .value {
  font-weight: bold;
  color: #303133;
}

.upload-demo {
  text-align: center;
}
</style> 