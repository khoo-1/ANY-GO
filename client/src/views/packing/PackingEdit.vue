<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>{{ isEdit ? '编辑装箱单' : '新增装箱单' }}</h2>
      </div>
      <div class="header-actions">
        <el-upload
          class="upload-demo"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          accept=".xlsx,.xls"
          :on-change="handleImportFile"
        >
          <el-button>导入Excel</el-button>
        </el-upload>
        <el-button @click="generatePackingListTemplate">
          <el-icon><Download /></el-icon>
          下载模板
        </el-button>
        <el-button @click="showImportHistory = true">导入历史</el-button>
        <el-button @click="router.back()">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存
        </el-button>
      </div>
    </div>

    <el-form 
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      v-loading="loading"
    >
      <el-card>
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="店铺名称" prop="storeName">
              <el-input v-model="form.storeName" placeholder="请输入店铺名称" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="类型" prop="type">
              <el-select v-model="form.type" placeholder="请选择类型">
                <el-option label="普货" value="普货" />
                <el-option label="纺织" value="纺织" />
                <el-option label="混装" value="混装" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备注" prop="remarks">
              <el-input v-model="form.remarks" placeholder="请输入备注" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 商品明细 -->
      <el-card class="mt-4">
        <template #header>
          <div class="card-header">
            <span>商品明细</span>
            <el-button type="primary" @click="showProductDialog">
              添加商品
            </el-button>
          </div>
        </template>

        <el-table :data="form.items" border>
          <el-table-column prop="product.sku" label="SKU" width="150" />
          <el-table-column prop="product.name" label="商品名称" min-width="200" />
          <el-table-column prop="product.chineseName" label="中文名称" min-width="200" />
          <el-table-column prop="quantity" label="总数量" width="120">
            <template #default="{ row }">
              {{ calculateTotalQuantity(row.boxQuantities) }}
            </template>
          </el-table-column>
          <el-table-column label="装箱明细" min-width="300">
            <template #default="{ row }">
              <div class="box-quantities">
                <el-tag 
                  v-for="(box, index) in row.boxQuantities"
                  :key="index"
                  closable
                  @close="removeBoxQuantity(row, index)"
                >
                  {{ box.boxNo }}: {{ box.quantity }}件
                </el-tag>
                <el-button link type="primary" @click="showBoxDialog(row)">
                  添加
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ $index }">
              <el-button link type="danger" @click="removeItem($index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 箱子规格 -->
      <el-card class="mt-4">
        <template #header>
          <div class="card-header">
            <span>箱子规格</span>
            <el-button type="primary" @click="addBoxSpec">
              添加箱子
            </el-button>
          </div>
        </template>

        <el-table :data="form.boxSpecs" border>
          <el-table-column type="index" label="箱号" width="80" />
          <el-table-column label="尺寸(cm)" width="400">
            <template #default="{ row }">
              <el-input-number 
                v-model="row.length" 
                :min="0" 
                :precision="1"
                placeholder="长"
                style="width: 120px"
                @change="calculateVolume(row)"
              />
              ×
              <el-input-number 
                v-model="row.width" 
                :min="0" 
                :precision="1"
                placeholder="宽"
                style="width: 120px"
                @change="calculateVolume(row)"
              />
              ×
              <el-input-number 
                v-model="row.height" 
                :min="0" 
                :precision="1"
                placeholder="高"
                style="width: 120px"
                @change="calculateVolume(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="重量(kg)" width="150">
            <template #default="{ row }">
              <el-input-number 
                v-model="row.weight" 
                :min="0" 
                :precision="2"
                style="width: 120px"
              />
            </template>
          </el-table-column>
          <el-table-column label="体积(m³)" width="150">
            <template #default="{ row }">
              {{ row.volume?.toFixed(3) || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="边体积(m³)" width="150">
            <template #default="{ row }">
              {{ row.edgeVolume?.toFixed(3) || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="总件数" width="120">
            <template #default="{ row }">
              {{ calculateBoxTotalPieces(row) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ $index }">
              <el-button 
                link 
                type="danger" 
                @click="removeBoxSpec($index)"
                :disabled="hasBoxQuantities($index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-form>

    <!-- 选择商品对话框 -->
    <el-dialog
      v-model="productDialogVisible"
      title="选择商品"
      width="800px"
      destroy-on-close
    >
      <div class="dialog-search">
        <el-input
          v-model="productSearch"
          placeholder="输入SKU或名称搜索"
          clearable
          @input="debouncedSearch"
        >
          <template #append>
            <el-button @click="debouncedSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>

      <el-table
        :data="productList"
        v-loading="searching"
        :height="virtualScrollProps.height"
        :virtual-scrolling="true"
        :item-size="virtualScrollProps.itemSize"
        border
        @row-click="handleProductSelect"
      >
        <el-table-column prop="sku" label="SKU" width="150" />
        <el-table-column prop="name" label="商品名称" min-width="200" />
        <el-table-column prop="chineseName" label="中文名称" min-width="200" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="stock" label="库存" width="100" />
      </el-table>

      <template #footer>
        <el-button @click="productDialogVisible = false">取消</el-button>
      </template>
    </el-dialog>

    <!-- 装箱数量对话框 -->
    <el-dialog
      v-model="boxDialogVisible"
      title="添加装箱数量"
      width="500px"
      destroy-on-close
    >
      <el-form :model="boxForm" label-width="100px">
        <el-form-item label="选择箱子">
          <el-select v-model="boxForm.boxNo" placeholder="请选择箱子">
            <el-option
              v-for="option in boxNoOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number 
            v-model="boxForm.quantity" 
            :min="1" 
            :precision="0"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="boxDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBoxQuantity">
          确定
        </el-button>
      </template>
    </el-dialog>

    <ImportHistoryDialog />
    <ImportProgress />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Search, Download } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import type { 
  PackingList, 
  PackingListItem,
  BoxQuantity,
  BoxSpecs,
  Product 
} from '@/types/packing'
import packingApi from '@/api/packing'
import productApi from '@/api/product'
import { usePackingStore } from '@/stores/packing'
import { generatePackingListTemplate, validatePackingListExcel } from '@/utils/excel'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)

// 是否是编辑模式
const isEdit = computed(() => route.params.id !== undefined)

// 表单数据
const form = reactive({
  storeName: '',
  type: '',
  remarks: '',
  items: [] as PackingListItem[],
  boxSpecs: [] as BoxSpecs[]
})

// 表单验证规则
const rules = {
  storeName: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }]
}

// 商品选择相关
const productDialogVisible = ref(false)
const productSearch = ref('')
const productList = ref<Product[]>([])
const currentEditingItem = ref<PackingListItem>()

// 装箱数量相关
const boxDialogVisible = ref(false)
const boxForm = reactive({
  boxNo: '',
  quantity: 1
})

// 导入相关
const importing = ref(false)
const importProgress = ref(0)
const showImportHistory = ref(false)

// 添加store
const packingStore = usePackingStore()

// 处理文件导入
async function handleImportFile(file: File) {
  if (!file) return

  const isExcel = [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ].includes(file.type)

  if (!isExcel) {
    ElMessage.error('请上传Excel文件')
    return
  }

  try {
    // 先验证Excel数据
    const validation = await validatePackingListExcel(file)
    if (!validation.valid) {
      ElMessageBox.alert(validation.errors.join('\n'), '导入验证失败', {
        type: 'error'
      })
      return
    }

    const startTime = performance.now()
    importing.value = true
    importProgress.value = 0
    
    const formData = new FormData()
    formData.append('file', file)
    
    const result = await packingApi.import(formData, (progress) => {
      importProgress.value = progress
    })

    if (result.success) {
      ElMessage.success('导入成功')
      // 更新表单数据
      if (result.data) {
        Object.assign(form, {
          storeName: result.data.storeName,
          type: result.data.type,
          remarks: result.data.remarks,
          items: result.data.items,
          boxSpecs: result.data.boxSpecs
        })
        // 保存为模板
        packingStore.addTemplate(result.data)
      }

      // 记录导入历史
      packingStore.addImportHistory({
        filename: file.name,
        success: true
      })
    } else {
      ElMessageBox.alert(result.errors.join('\n'), '导入失败', {
        type: 'error'
      })
      // 记录导入历史
      packingStore.addImportHistory({
        filename: file.name,
        success: false,
        errors: result.errors
      })
    }

    // 记录性能指标
    const endTime = performance.now()
    packingStore.recordPerformance('importTime', endTime - startTime)
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
    // 记录导入历史
    packingStore.addImportHistory({
      filename: file.name,
      success: false,
      errors: [error.message]
    })
  } finally {
    importing.value = false
    importProgress.value = 0
  }
}

// 性能优化：防抖搜索
const searchTimeout = ref<number>()
function debouncedSearch() {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  searchTimeout.value = window.setTimeout(() => {
    searchProducts()
  }, 300)
}

// 性能优化：虚拟滚动相关
const virtualScrollProps = {
  itemSize: 40,
  height: 400
}

// 性能优化：计算属性缓存
const boxNoOptions = computed(() => {
  return form.boxSpecs.map((_, index) => ({
    label: `箱${index + 1}`,
    value: `箱${index + 1}`
  }))
})

// 清理定时器
onBeforeUnmount(() => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
})

// 加载数据
async function loadData() {
  if (!isEdit.value) return

  const id = Number(route.params.id)
  if (!id) return

  const startTime = performance.now()
  loading.value = true
  
  try {
    const data = await packingApi.get(id)
    Object.assign(form, {
      storeName: data.storeName,
      type: data.type,
      remarks: data.remarks,
      items: data.items,
      boxSpecs: data.boxSpecs
    })
  } catch (error) {
    console.error('加载装箱单失败:', error)
    ElMessage.error('加载装箱单失败')
  } finally {
    loading.value = false
    const endTime = performance.now()
    packingStore.recordPerformance('loadTime', endTime - startTime)
  }
}

// 搜索商品
const searching = ref(false)
async function searchProducts() {
  const startTime = performance.now()
  searching.value = true

  // 先从缓存中查找
  const cachedResults = packingStore.cachedProducts.filter(product => 
    product.sku.toLowerCase().includes(productSearch.value.toLowerCase()) ||
    product.name.toLowerCase().includes(productSearch.value.toLowerCase())
  )

  if (cachedResults.length > 0) {
    productList.value = cachedResults
    searching.value = false
    return
  }

  try {
    const res = await productApi.list({
      keyword: productSearch.value,
      pageSize: 10
    })
    productList.value = res.items
    // 缓存搜索结果
    packingStore.cacheProducts(res.items)
  } catch (error) {
    console.error('搜索商品失败:', error)
    ElMessage.error('搜索商品失败')
  } finally {
    searching.value = false
    const endTime = performance.now()
    packingStore.recordPerformance('searchTime', endTime - startTime)
  }
}

// 选择商品
function handleProductSelect(product: Product) {
  const existingItem = form.items.find(item => item.productId === product.id)
  if (existingItem) {
    ElMessage.warning('该商品已添加')
    return
  }

  form.items.push({
    productId: product.id,
    product,
    quantity: 0,
    boxQuantities: [],
    weight: 0,
    volume: 0
  })

  productDialogVisible.value = false
}

// 显示商品选择对话框
function showProductDialog() {
  productSearch.value = ''
  productList.value = []
  productDialogVisible.value = true
}

// 显示装箱对话框
function showBoxDialog(item: PackingListItem) {
  if (!form.boxSpecs.length) {
    ElMessage.warning('请先添加箱子规格')
    return
  }

  currentEditingItem.value = item
  boxForm.boxNo = ''
  boxForm.quantity = 1
  boxDialogVisible.value = true
}

// 确认装箱数量
function confirmBoxQuantity() {
  if (!boxForm.boxNo || !currentEditingItem.value) return

  const existingBox = currentEditingItem.value.boxQuantities.find(
    box => box.boxNo === boxForm.boxNo
  )

  if (existingBox) {
    existingBox.quantity = boxForm.quantity
  } else {
    currentEditingItem.value.boxQuantities.push({
      boxNo: boxForm.boxNo,
      quantity: boxForm.quantity
    })
  }

  boxDialogVisible.value = false
  calculateItemQuantity(currentEditingItem.value)
}

// 移除装箱数量
function removeBoxQuantity(item: PackingListItem, index: number) {
  item.boxQuantities.splice(index, 1)
  calculateItemQuantity(item)
}

// 移除商品
function removeItem(index: number) {
  form.items.splice(index, 1)
}

// 添加箱子规格
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

// 移除箱子规格
function removeBoxSpec(index: number) {
  form.boxSpecs.splice(index, 1)
}

// 计算体积
function calculateVolume(box: BoxSpecs) {
  if (box.length && box.width && box.height) {
    // 转换为米
    const l = box.length / 100
    const w = box.width / 100
    const h = box.height / 100
    box.volume = l * w * h
    box.edgeVolume = (l + 0.02) * (w + 0.02) * (h + 0.02)
  }
}

// 计算商品总数量
function calculateTotalQuantity(boxQuantities: BoxQuantity[]) {
  return boxQuantities.reduce((sum, box) => sum + box.quantity, 0)
}

// 计算箱子总件数
function calculateBoxTotalPieces(box: BoxSpecs) {
  return form.items.reduce((sum, item) => {
    const boxQuantity = item.boxQuantities.find(q => q.boxNo === `箱${form.boxSpecs.indexOf(box) + 1}`)
    return sum + (boxQuantity?.quantity || 0)
  }, 0)
}

// 计算商品数量
function calculateItemQuantity(item: PackingListItem) {
  item.quantity = calculateTotalQuantity(item.boxQuantities)
}

// 检查箱子是否被使用
function hasBoxQuantities(boxIndex: number) {
  const boxNo = `箱${boxIndex + 1}`
  return form.items.some(item =>
    item.boxQuantities.some(box => box.boxNo === boxNo)
  )
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    if (!form.items.length) {
      ElMessage.warning('请添加商品')
      return
    }

    if (!form.boxSpecs.length) {
      ElMessage.warning('请添加箱子规格')
      return
    }

    const invalidItem = form.items.find(item => !item.boxQuantities.length)
    if (invalidItem) {
      ElMessage.warning(`商品 ${invalidItem.product.name} 未添加装箱数量`)
      return
    }

    const startTime = performance.now()
    submitting.value = true
    
    if (isEdit.value) {
      await packingApi.update(Number(route.params.id), form)
      ElMessage.success('更新成功')
    } else {
      await packingApi.create(form)
      ElMessage.success('创建成功')
      // 保存为模板
      packingStore.addTemplate(form)
    }
    
    const endTime = performance.now()
    packingStore.recordPerformance('saveTime', endTime - startTime)
    
    router.back()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

// 添加导入历史对话框组件
const ImportHistoryDialog = defineComponent({
  setup() {
    const history = computed(() => packingStore.importHistory)
    
    return () => (
      <el-dialog
        modelValue={showImportHistory.value}
        title="导入历史"
        width="600px"
        onUpdate:modelValue={(val: boolean) => showImportHistory.value = val}
      >
        <el-table data={history.value} border>
          <el-table-column prop="filename" label="文件名" />
          <el-table-column prop="timestamp" label="时间" formatter={(row: any) => 
            new Date(row.timestamp).toLocaleString()
          } />
          <el-table-column prop="success" label="状态">
            {{
              default: ({ row }: any) => (
                <el-tag type={row.success ? 'success' : 'danger'}>
                  {row.success ? '成功' : '失败'}
                </el-tag>
              )
            }}
          </el-table-column>
          <el-table-column label="操作" width="100">
            {{
              default: ({ row }: any) => row.errors && (
                <el-button
                  link
                  type="primary"
                  onClick={() => {
                    ElMessageBox.alert(row.errors.join('\n'), '错误详情')
                  }}
                >
                  查看错误
                </el-button>
              )
            }}
          </el-table-column>
        </el-table>
      </el-dialog>
    )
  }
})

// 添加导入进度条组件
const ImportProgress = defineComponent({
  setup() {
    return () => importing.value && (
      <div class="import-progress">
        <el-progress 
          percentage={importProgress.value}
          status={importProgress.value === 100 ? 'success' : ''}
        />
      </div>
    )
  }
})

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

.mt-4 {
  margin-top: 16px;
}

.dialog-search {
  margin-bottom: 16px;
}

.box-quantities {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.import-progress {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 200px;
  z-index: 2000;
  background: white;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style> 