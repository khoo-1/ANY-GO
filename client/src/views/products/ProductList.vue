<template>
  <div class="page-container">
    <div class="page-header">
      <h2>商品列表</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd">新增商品</el-button>
        <el-button @click="showExportDialog">导出</el-button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <el-form :model="searchForm" inline>
      <el-form-item label="关键词">
        <el-input v-model="searchForm.keyword" placeholder="SKU/名称" />
      </el-form-item>
      <el-form-item label="类型">
        <el-select v-model="searchForm.type" clearable>
          <el-option label="普货" value="普货" />
          <el-option label="纺织" value="纺织" />
          <el-option label="混装" value="混装" />
        </el-select>
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="searchForm.category" clearable>
          <el-option 
            v-for="category in categories" 
            :key="category" 
            :label="category" 
            :value="category" 
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" clearable>
          <el-option label="正常" value="active" />
          <el-option label="禁用" value="inactive" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 数据表格 -->
    <el-table 
      v-loading="loading"
      :data="tableData"
      border
      style="width: 100%"
    >
      <el-table-column prop="sku" label="SKU" width="120" />
      <el-table-column prop="name" label="商品名称" min-width="200">
        <template #default="{ row }">
          <div>{{ row.name }}</div>
          <div class="text-gray">{{ row.chineseName }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="100" />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column prop="price" label="价格" width="100">
        <template #default="{ row }">
          {{ row.price.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="100">
        <template #default="{ row }">
          <span :class="{ 'text-danger': row.stock <= row.alertThreshold }">
            {{ row.stock }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="handleStock(row)">库存</el-button>
          <el-popconfirm
            title="确定要删除该商品吗？"
            @confirm="handleDelete(row)"
          >
            <template #reference>
              <el-button link type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 商品表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增商品' : '编辑商品'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="SKU" prop="sku">
          <el-input v-model="form.sku" :disabled="dialogType === 'edit'" />
        </el-form-item>
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="中文名称" prop="chineseName">
          <el-input v-model="form.chineseName" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type">
            <el-option label="普货" value="普货" />
            <el-option label="纺织" value="纺织" />
            <el-option label="混装" value="混装" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select 
            v-model="form.category"
            filterable
            allow-create
            default-first-option
          >
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="form.price" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="成本" prop="cost">
          <el-input-number v-model="form.cost" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="库存预警" prop="alertThreshold">
          <el-input-number v-model="form.alertThreshold" :min="0" />
        </el-form-item>
        <el-form-item label="供应商" prop="supplier">
          <el-select
            v-model="form.supplier"
            filterable
            allow-create
            default-first-option
            clearable
          >
            <el-option
              v-for="supplier in suppliers"
              :key="supplier"
              :label="supplier"
              :value="supplier"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status" v-if="dialogType === 'edit'">
          <el-radio-group v-model="form.status">
            <el-radio label="active">正常</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 库存操作对话框 -->
    <el-dialog
      v-model="stockDialogVisible"
      title="库存操作"
      width="400px"
    >
      <el-form
        ref="stockFormRef"
        :model="stockForm"
        :rules="stockRules"
        label-width="100px"
      >
        <el-form-item label="当前库存">
          <span>{{ currentProduct?.stock || 0 }}</span>
        </el-form-item>
        <el-form-item label="操作类型" prop="type">
          <el-select v-model="stockForm.type">
            <el-option label="入库" value="入库" />
            <el-option label="出库" value="出库" />
            <el-option label="调整" value="调整" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="stockForm.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="备注" prop="reason">
          <el-input
            v-model="stockForm.reason"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleStockSubmit"
          :loading="stockSubmitting"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 导出对话框 -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出商品"
      width="400px"
    >
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="导出字段">
          <el-checkbox-group v-model="exportForm.fields">
            <el-checkbox label="sku">SKU</el-checkbox>
            <el-checkbox label="name">商品名称</el-checkbox>
            <el-checkbox label="chineseName">中文名称</el-checkbox>
            <el-checkbox label="type">类型</el-checkbox>
            <el-checkbox label="category">分类</el-checkbox>
            <el-checkbox label="price">价格</el-checkbox>
            <el-checkbox label="cost">成本</el-checkbox>
            <el-checkbox label="stock">库存</el-checkbox>
            <el-checkbox label="supplier">供应商</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleExport"
          :loading="exporting"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { searchProducts, exportProducts } from '@/api/product'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import type { Product } from '@/types/product'
import { ElVirtualList } from 'element-plus'
import productApi from '@/api/product'

// 搜索表单
const searchForm = reactive({
  keyword: '',
  type: '',
  category: '',
  status: '',
  page: 1,
  pageSize: 20
})

// 表格数据
const tableData = ref<Product[]>([])
const total = ref(0)
const loading = ref(false)

// 类别和供应商列表
const categories = ref<string[]>([])
const suppliers = ref<string[]>([])

// 商品表单对话框
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const submitting = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({
  sku: '',
  name: '',
  chineseName: '',
  type: '普货',
  category: '',
  price: 0,
  cost: 0,
  alertThreshold: 10,
  supplier: '',
  status: 'active'
})

// 表单验证规则
const rules = {
  sku: [
    { required: true, message: '请输入SKU', trigger: 'blur' },
    { min: 3, max: 50, message: 'SKU长度在3-50个字符之间', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' },
    { min: 1, max: 200, message: '商品名称长度在1-200个字符之间', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择商品类型', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入商品价格', trigger: 'blur' }
  ]
}

// 库存操作对话框
const stockDialogVisible = ref(false)
const stockSubmitting = ref(false)
const stockFormRef = ref<FormInstance>()
const currentProduct = ref<Product>()
const stockForm = reactive({
  type: '入库',
  quantity: 1,
  reason: ''
})

// 库存表单验证规则
const stockRules = {
  type: [
    { required: true, message: '请选择操作类型', trigger: 'change' }
  ],
  quantity: [
    { required: true, message: '请输入数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '数量必须大于0', trigger: 'blur' }
  ]
}

// 导出对话框
const exportDialogVisible = ref(false)
const exporting = ref(false)
const exportForm = reactive({
  fields: ['sku', 'name', 'chineseName', 'type', 'category', 'price', 'stock']
})

// 初始化
onMounted(async () => {
  await Promise.all([
    loadCategories(),
    loadSuppliers()
  ])
  await loadData()
})

// 加载类别列表
async function loadCategories() {
  try {
    categories.value = await productApi.getCategories()
  } catch (error) {
    console.error('加载类别列表失败:', error)
  }
}

// 加载供应商列表
async function loadSuppliers() {
  try {
    suppliers.value = await productApi.getSuppliers()
  } catch (error) {
    console.error('加载供应商列表失败:', error)
  }
}

// 加载表格数据
async function loadData() {
  loading.value = true
  try {
    const res = await productApi.list({
      page: searchForm.page,
      pageSize: searchForm.pageSize,
      ...searchForm
    })
    tableData.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
function handleSearch() {
  searchForm.page = 1
  loadData()
}

// 重置搜索
function handleReset() {
  Object.assign(searchForm, {
    keyword: '',
    type: '',
    category: '',
    status: ''
  })
  handleSearch()
}

// 新增商品
function handleAdd() {
  dialogType.value = 'add'
  Object.assign(form, {
    sku: '',
    name: '',
    chineseName: '',
    type: '普货',
    category: '',
    price: 0,
    cost: 0,
    alertThreshold: 10,
    supplier: '',
    status: 'active'
  })
  dialogVisible.value = true
}

// 编辑商品
function handleEdit(row: Product) {
  dialogType.value = 'edit'
  Object.assign(form, {
    sku: row.sku,
    name: row.name,
    chineseName: row.chineseName,
    type: row.type,
    category: row.category,
    price: row.price,
    cost: row.cost,
    alertThreshold: row.alertThreshold,
    supplier: row.supplier,
    status: row.status
  })
  dialogVisible.value = true
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate()
  
  submitting.value = true
  try {
    if (dialogType.value === 'add') {
      await productApi.create(form)
      ElMessage.success('创建成功')
    } else {
      await productApi.update(Number(currentProduct.value?.id), form)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 删除商品
async function handleDelete(row: Product) {
  try {
    await productApi.delete(row.id)
    ElMessage.success('删除成功')
    if (tableData.value.length === 1 && searchForm.page > 1) {
      searchForm.page--
    }
    loadData()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

// 库存操作
function handleStock(row: Product) {
  currentProduct.value = row
  Object.assign(stockForm, {
    type: '入库',
    quantity: 1,
    reason: ''
  })
  stockDialogVisible.value = true
}

// 提交库存操作
async function handleStockSubmit() {
  if (!stockFormRef.value || !currentProduct.value) return
  
  await stockFormRef.value.validate()
  
  stockSubmitting.value = true
  try {
    await productApi.updateStock(currentProduct.value.id, stockForm)
    ElMessage.success('操作成功')
    stockDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  } finally {
    stockSubmitting.value = false
  }
}

// 显示导出对话框
function showExportDialog() {
  exportDialogVisible.value = true
}

// 导出数据
async function handleExport() {
  exporting.value = true
  try {
    const blob = await productApi.export({
      ...searchForm,
      fields: exportForm.fields
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `商品列表_${new Date().toLocaleDateString()}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    exportDialogVisible.value = false
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 分页
function handleSizeChange(val: number) {
  searchForm.pageSize = val
  loadData()
}

function handleCurrentChange(val: number) {
  searchForm.page = val
  loadData()
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}

.text-danger {
  color: #f56c6c;
}

:deep(.el-table) {
  margin-top: 20px;
}

:deep(.el-form--inline .el-form-item) {
  margin-right: 16px;
}
</style> 