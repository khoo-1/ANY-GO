import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'

// 生成装箱单Excel模板
export function generatePackingListTemplate() {
  const template = [
    ['店铺名称', '', '类型', '普货'],  // A1-D1
    ['总箱数', '', '总重量(kg)', ''],  // A2-D2
    ['总体积(m³)', '', '总边加一体积(m³)', ''],  // A3-D3
    ['总件数', '', '', ''],  // A4-D4
    ['', '', '', ''],  // A5-D5 空行
    ['SKU', '中文名称', '数量', '箱号', '装箱数量', '规格说明'],  // A6-F6 表头
  ]

  // 创建工作簿
  const wb = XLSX.utils.book_new()
  
  // 创建主工作表
  const ws = XLSX.utils.aoa_to_sheet(template)
  
  // 设置列宽
  const colWidths = [
    { wch: 15 },  // SKU
    { wch: 30 },  // 中文名称
    { wch: 10 },  // 数量
    { wch: 10 },  // 箱号
    { wch: 10 },  // 装箱数量
    { wch: 20 },  // 规格说明
  ]
  ws['!cols'] = colWidths

  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(wb, ws, '装箱单')

  // 创建常用箱规工作表
  const boxSpecsTemplate = [
    ['箱号', '长(cm)', '宽(cm)', '高(cm)', '重量(kg)', '体积(m³)', '边加一体积(m³)', '总件数'],
    ['1#', 60, 40, 40, 15, 0.096, 0.1152, 100],
    ['2#', 50, 40, 30, 12, 0.06, 0.072, 80],
    ['3#', 40, 30, 30, 8, 0.036, 0.0432, 50],
  ]
  const wsBoxSpecs = XLSX.utils.aoa_to_sheet(boxSpecsTemplate)
  
  // 设置列宽
  wsBoxSpecs['!cols'] = [
    { wch: 10 },  // 箱号
    { wch: 10 },  // 长
    { wch: 10 },  // 宽
    { wch: 10 },  // 高
    { wch: 10 },  // 重量
    { wch: 10 },  // 体积
    { wch: 12 },  // 边加一体积
    { wch: 10 },  // 总件数
  ]

  // 添加常用箱规工作表
  XLSX.utils.book_append_sheet(wb, wsBoxSpecs, '常用箱规')

  // 导出Excel文件
  const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  saveAs(blob, '装箱单导入模板.xlsx')
}

// 验证装箱单Excel数据
export function validatePackingListExcel(file: File): Promise<{
  valid: boolean
  errors: string[]
}> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const buffer = new Uint8Array(e.target?.result as ArrayBuffer)
        const workbook = XLSX.read(buffer, { type: 'array' })

        const errors: string[] = []

        // 1. 验证文件名格式
        if (!file.name.match(/^.+海运ERP\.xlsx?$/i)) {
          errors.push('文件名格式不正确，应为：{店铺名}海运ERP.xlsx')
        }

        // 2. 验证工作表
        const mainSheet = workbook.Sheets[workbook.SheetNames[0]]
        if (!mainSheet) {
          errors.push('Excel文件格式不正确：找不到主工作表')
          resolve({ valid: false, errors })
          return
        }

        // 3. 验证必要字段
        const requiredFields = ['SKU', '中文名称', '数量', '箱号', '装箱数量']
        const headers = XLSX.utils.sheet_to_json(mainSheet, { header: 1 })[5] || []
        
        for (const field of requiredFields) {
          if (!headers.includes(field)) {
            errors.push(`Excel文件缺少必要列：${field}`)
          }
        }

        // 4. 验证数据有效性
        const rows = XLSX.utils.sheet_to_json(mainSheet, { range: 6 })
        if (rows.length === 0) {
          errors.push('Excel文件中没有商品数据')
        }

        resolve({
          valid: errors.length === 0,
          errors
        })
      } catch (error) {
        reject(error)
      }
    }
    reader.onerror = reject
    reader.readAsArrayBuffer(file)
  })
} 