import React from 'react';
import { Button, Upload, message } from 'antd';
import { UploadOutlined, DownloadOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import * as XLSX from 'xlsx';
import FileSaver from 'file-saver';
import axios from 'axios';
import { Product } from '../../types';

interface Props {
  onSuccess: () => void;
}

const BatchOperations = ({ onSuccess }: Props) => {
  const handleExport = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/products');
      const products: Product[] = response.data;

      // 准备导出数据
      const exportData = products.map(product => ({
        SKU: product.sku,
        商品名称: product.name,
        描述: product.description || '',
        类别: product.category || '',
        售价: product.price,
        成本价: product.cost || '',
        库存: product.stock,
        库存预警阈值: product.alertThreshold || '',
        供应商: product.supplier || ''
      }));

      // 创建工作簿
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(exportData);

      // 设置列宽
      const colWidths = [
        { wch: 15 }, // SKU
        { wch: 30 }, // 商品名称
        { wch: 40 }, // 描述
        { wch: 15 }, // 类别
        { wch: 10 }, // 售价
        { wch: 10 }, // 成本价
        { wch: 10 }, // 库存
        { wch: 15 }, // 库存预警阈值
        { wch: 20 }  // 供应商
      ];
      ws['!cols'] = colWidths;

      XLSX.utils.book_append_sheet(wb, ws, "商品列表");

      // 生成Excel文件并下载
      const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      FileSaver.saveAs(blob, `商品列表_${new Date().toLocaleDateString()}.xlsx`);

      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const uploadProps: UploadProps = {
    name: 'file',
    action: 'http://localhost:5000/api/products/batch',
    accept: '.xlsx,.xls',
    showUploadList: false,
    onChange(info) {
      if (info.file.status === 'done') {
        message.success('导入成功');
        onSuccess();
      } else if (info.file.status === 'error') {
        message.error('导入失败');
      }
    },
  };

  return (
    <div style={{ marginBottom: 16 }}>
      <Upload {...uploadProps}>
        <Button icon={<UploadOutlined />}>批量导入</Button>
      </Upload>
      <Button 
        icon={<DownloadOutlined />} 
        onClick={handleExport}
        style={{ marginLeft: 8 }}
      >
        批量导出
      </Button>
      <Button 
        type="link" 
        onClick={() => {
          const templateWb = XLSX.utils.book_new();
          const templateWs = XLSX.utils.json_to_sheet([{
            SKU: '',
            商品名称: '',
            描述: '',
            类别: '',
            售价: '',
            成本价: '',
            库存: '',
            库存预警阈值: '',
            供应商: ''
          }]);
          XLSX.utils.book_append_sheet(templateWb, templateWs, "模板");
          const buffer = XLSX.write(templateWb, { bookType: 'xlsx', type: 'array' });
          const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
          FileSaver.saveAs(blob, '商品导入模板.xlsx');
        }}
      >
        下载导入模板
      </Button>
    </div>
  );
};

export default BatchOperations; 