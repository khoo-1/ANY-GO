import React, { useState, useEffect } from 'react';
import { Table, Button, Space, message, Modal, Input, Select, Upload } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined, SearchOutlined } from '@ant-design/icons';
import { Product, ProductQuery } from '../../types/api';
import { productService } from '../../services/productService';
import ProductForm from '../product/ProductForm';
import { handleError } from '../../utils/errorHandler';
import { AxiosError } from 'axios';
import { ApiResponse } from '../../types';

const { Search } = Input;

const Products: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState<ProductQuery>({ page: 1, pageSize: 10 });
  const [visible, setVisible] = useState(false);
  const [currentProduct, setCurrentProduct] = useState<Product | null>(null);
  const [importVisible, setImportVisible] = useState(false);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const res = await productService.list(query);
      setProducts(res.data.items);
      setTotal(res.data.pagination.total);
    } catch (error) {
      handleError(error as AxiosError<ApiResponse> | Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, [query]);

  const handleDelete = async (id: string) => {
    try {
      await productService.delete(id);
      message.success('删除成功');
      loadProducts();
    } catch (error) {
      handleError(error as AxiosError<ApiResponse> | Error);
    }
  };

  const handleSearch = (value: string) => {
    setQuery({ ...query, page: 1, keyword: value });
  };

  const handleTypeFilter = (value: Product['type'] | undefined) => {
    setQuery({ ...query, page: 1, type: value });
  };

  const handleImport = async (file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      await productService.importProducts(formData);
      message.success('导入成功');
      loadProducts();
      setImportVisible(false);
    } catch (error) {
      handleError(error as AxiosError<ApiResponse> | Error);
    }
  };

  const columns = [
    { 
      title: 'SKU',
      dataIndex: 'sku',
      key: 'sku',
      width: 150,
      fixed: 'left' as const
    },
    { 
      title: '商品名称',
      dataIndex: 'name',
      key: 'name',
      width: 200
    },
    { 
      title: '中文名称',
      dataIndex: 'chineseName',
      key: 'chineseName',
      width: 200
    },
    { 
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      filters: [
        { text: '普货', value: '普货' },
        { text: '纺织', value: '纺织' },
        { text: '混装', value: '混装' }
      ],
      onFilter: (value: any, record: Product) => record.type === value
    },
    { 
      title: '类别',
      dataIndex: 'category',
      key: 'category',
      width: 150
    },
    { 
      title: '售价',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => `¥${price.toFixed(2)}`
    },
    { 
      title: '成本价',
      dataIndex: 'cost',
      key: 'cost',
      width: 100,
      render: (cost: number) => `¥${cost?.toFixed(2) || '-'}`
    },
    { 
      title: '库存',
      dataIndex: 'stock',
      key: 'stock',
      width: 100
    },
    { 
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <span style={{ color: status === 'active' ? '#52c41a' : '#ff4d4f' }}>
          {status === 'active' ? '上架' : '下架'}
        </span>
      )
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right' as const,
      width: 200,
      render: (_: unknown, record: Product) => (
        <Space>
          <Button 
            icon={<EditOutlined />} 
            onClick={() => {
              setCurrentProduct(record);
              setVisible(true);
            }}
          >
            编辑
          </Button>
          <Button 
            icon={<DeleteOutlined />} 
            danger
            onClick={() => {
              Modal.confirm({
                title: '确认删除',
                content: '确定要删除这个商品吗？',
                onOk: () => handleDelete(record.id)
              });
            }}
          >
            删除
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => {
              setCurrentProduct(null);
              setVisible(true);
            }}
          >
            添加商品
          </Button>
          <Button 
            icon={<UploadOutlined />}
            onClick={() => setImportVisible(true)}
          >
            批量导入
          </Button>
          <Select
            style={{ width: 120 }}
            placeholder="商品类型"
            allowClear
            onChange={handleTypeFilter}
          >
            <Select.Option value="普货">普货</Select.Option>
            <Select.Option value="纺织">纺织</Select.Option>
            <Select.Option value="混装">混装</Select.Option>
          </Select>
        </Space>
        <Search
          placeholder="搜索SKU/商品名称"
          allowClear
          enterButton={<SearchOutlined />}
          onSearch={handleSearch}
          style={{ width: 300 }}
        />
      </div>

      <Table
        loading={loading}
        columns={columns}
        dataSource={products}
        rowKey="id"
        scroll={{ x: 1500 }}
        pagination={{
          total,
          current: query.page,
          pageSize: query.pageSize,
          onChange: (page, pageSize) => setQuery({ ...query, page, pageSize })
        }}
      />

      <ProductForm
        visible={visible}
        product={currentProduct}
        onCancel={() => setVisible(false)}
        onSuccess={() => {
          setVisible(false);
          loadProducts();
        }}
      />

      <Modal
        title="批量导入商品"
        open={importVisible}
        onCancel={() => setImportVisible(false)}
        footer={null}
      >
        <Upload.Dragger
          name="file"
          accept=".xlsx,.xls"
          showUploadList={false}
          customRequest={({ file }) => handleImport(file as File)}
        >
          <p className="ant-upload-drag-icon">
            <UploadOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持 .xlsx, .xls 格式的文件
          </p>
        </Upload.Dragger>
      </Modal>
    </div>
  );
};

export default Products; 