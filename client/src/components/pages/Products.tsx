import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Space, 
  message, 
  Modal, 
  Input, 
  Select, 
  Upload, 
  Typography,
  Card,
  Form,
  Row,
  Col,
  Popconfirm,
  Tag,
  InputNumber
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  UploadOutlined, 
  SearchOutlined,
  DownloadOutlined,
  FilterOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { Product, ProductQuery } from '../../types/api';
import { productService } from '../../services/productService';
import ProductForm from '../product/ProductForm';
import { handleError } from '../../utils/errorHandler';
import { AxiosError } from 'axios';
import { ApiResponse } from '../../types';
import type { UploadProps } from 'antd';
import ProductDetail from '../product/ProductDetail';

const { Search } = Input;
const { Title } = Typography;

const Products: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState<ProductQuery>({ page: 1, pageSize: 10 });
  const [visible, setVisible] = useState(false);
  const [currentProduct, setCurrentProduct] = useState<Product | null>(null);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [importResults, setImportResults] = useState<any>(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [advancedSearch, setAdvancedSearch] = useState(false);
  const [form] = Form.useForm();
  const [detailVisible, setDetailVisible] = useState(false);

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

  // 下载模板
  const handleDownloadTemplate = async () => {
    try {
      const response = await productService.downloadTemplate();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'product_import_template.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      message.error('下载模板失败');
    }
  };

  // 上传配置
  const uploadProps: UploadProps = {
    name: 'file',
    action: `${process.env.REACT_APP_API_URL}/api/products/import`,
    accept: '.xlsx,.xls',
    showUploadList: false,
    beforeUpload: (file) => {
      const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                      file.type === 'application/vnd.ms-excel';
      if (!isExcel) {
        message.error('只能上传 Excel 文件！');
        return Upload.LIST_IGNORE;
      }
      return true;
    },
    onChange: (info) => {
      if (info.file.status === 'uploading') {
        setLoading(true);
      }
      if (info.file.status === 'done') {
        setLoading(false);
        if (info.file.response) {
          setImportResults(info.file.response.results);
          setImportModalVisible(true);
          message.success(`成功导入 ${info.file.response.results.success.length} 条记录`);
        }
      }
      if (info.file.status === 'error') {
        setLoading(false);
        message.error('导入失败');
      }
    }
  };

  // 导入结果表格列配置
  const resultColumns = [
    {
      title: 'SKU',
      dataIndex: 'sku',
      key: 'sku',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (_: unknown, record: any) => record.error ? '失败' : '成功'
    },
    {
      title: '消息',
      dataIndex: 'message',
      key: 'message',
      render: (_: unknown, record: any) => record.error || record.message
    }
  ];

  // 批量删除
  const handleBatchDelete = async () => {
    try {
      await Promise.all(selectedRowKeys.map(id => productService.delete(id)));
      message.success('批量删除成功');
      setSelectedRowKeys([]);
      loadProducts();
    } catch (error) {
      handleError(error as AxiosError<ApiResponse> | Error);
    }
  };

  // 高级搜索
  const handleAdvancedSearch = async (values: any) => {
    setQuery({
      ...query,
      page: 1,
      ...values
    });
  };

  // 重置搜索
  const handleReset = () => {
    form.resetFields();
    setQuery({ page: 1, pageSize: 10 });
  };

  const columns = [
    { 
      title: 'SKU',
      dataIndex: 'sku',
      key: 'sku',
      width: 150,
      fixed: 'left' as const,
      render: (sku: string, record: Product) => (
        <a onClick={() => {
          setCurrentProduct(record);
          setDetailVisible(true);
        }}>
          {sku}
        </a>
      )
    },
    { 
      title: '中文名',
      dataIndex: 'chineseName',
      key: 'chineseName',
      width: 200
    },
    { 
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => {
        const colors = {
          '普货': 'blue',
          '纺织': 'green',
          '混装': 'orange'
        };
        return <Tag color={colors[type as keyof typeof colors]}>{type}</Tag>;
      }
    },
    { 
      title: '成本价',
      dataIndex: 'cost',
      key: 'cost',
      width: 100,
      align: 'right' as const,
      render: (cost: number) => `¥${cost.toFixed(2)}`
    },
    { 
      title: '头程运费',
      dataIndex: 'freightCost',
      key: 'freightCost',
      width: 100,
      align: 'right' as const,
      render: (freightCost: number) => `¥${freightCost.toFixed(2)}`
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right' as const,
      width: 180,
      render: (_: unknown, record: Product) => (
        <Space>
          <Button 
            type="link" 
            size="small"
            onClick={() => {
              setCurrentProduct(record);
              setDetailVisible(true);
            }}
          >
            查看
          </Button>
          <Button 
            type="link"
            size="small"
            onClick={() => {
              setCurrentProduct(record);
              setVisible(true);
            }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个商品吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              type="link"
              size="small"
              danger
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row gutter={[16, 16]} align="middle">
            <Col flex="auto">
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
                  icon={<DownloadOutlined />}
                  onClick={handleDownloadTemplate}
                >
                  下载导入模板
                </Button>
                <Upload {...uploadProps}>
                  <Button 
                    icon={<UploadOutlined />} 
                    loading={loading}
                  >
                    批量导入
                  </Button>
                </Upload>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={() => {
                    window.open(`${process.env.REACT_APP_API_URL}/api/products/export?${new URLSearchParams(query as any)}`);
                  }}
                >
                  导出列表
                </Button>
                {selectedRowKeys.length > 0 && (
                  <Popconfirm
                    title={`确定要删除选中的 ${selectedRowKeys.length} 个商品吗？`}
                    onConfirm={handleBatchDelete}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button danger>
                      批量删除
                    </Button>
                  </Popconfirm>
                )}
              </Space>
            </Col>
            <Col>
              <Space>
                <Button 
                  icon={<FilterOutlined />}
                  onClick={() => setAdvancedSearch(!advancedSearch)}
                >
                  高级筛选
                </Button>
                <Search
                  placeholder="搜索SKU/中文名"
                  allowClear
                  enterButton={<SearchOutlined />}
                  onSearch={handleSearch}
                  style={{ width: 300 }}
                />
              </Space>
            </Col>
          </Row>

          {advancedSearch && (
            <Card style={{ marginTop: 16 }}>
              <Form
                form={form}
                layout="inline"
                onFinish={handleAdvancedSearch}
              >
                <Form.Item name="type" label="商品类型">
                  <Select
                    style={{ width: 120 }}
                    allowClear
                    placeholder="选择类型"
                  >
                    <Select.Option value="普货">普货</Select.Option>
                    <Select.Option value="纺织">纺织</Select.Option>
                    <Select.Option value="混装">混装</Select.Option>
                  </Select>
                </Form.Item>
                <Form.Item name="minCost" label="最小成本价">
                  <InputNumber min={0} precision={2} />
                </Form.Item>
                <Form.Item name="maxCost" label="最大成本价">
                  <InputNumber min={0} precision={2} />
                </Form.Item>
                <Form.Item>
                  <Space>
                    <Button type="primary" htmlType="submit">
                      搜索
                    </Button>
                    <Button onClick={handleReset}>
                      重置
                    </Button>
                  </Space>
                </Form.Item>
              </Form>
            </Card>
          )}
        </div>

        <Table
          loading={loading}
          columns={columns}
          dataSource={products}
          rowKey="id"
          scroll={{ x: 1200 }}
          pagination={{
            total,
            current: query.page,
            pageSize: query.pageSize,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) => setQuery({ ...query, page, pageSize })
          }}
          rowSelection={{
            selectedRowKeys,
            onChange: (keys) => setSelectedRowKeys(keys as string[])
          }}
        />
      </Card>

      <ProductForm
        visible={visible}
        product={currentProduct}
        onCancel={() => setVisible(false)}
        onSuccess={() => {
          setVisible(false);
          loadProducts();
        }}
      />

      <ProductDetail
        visible={detailVisible}
        product={currentProduct}
        onClose={() => {
          setDetailVisible(false);
          setCurrentProduct(null);
        }}
      />

      <Modal
        title="导入结果"
        open={importModalVisible}
        onOk={() => setImportModalVisible(false)}
        onCancel={() => setImportModalVisible(false)}
        width={800}
      >
        {importResults && (
          <>
            <Title level={5}>
              成功：{importResults.success.length} 条，
              失败：{importResults.errors.length} 条
            </Title>
            <Table
              dataSource={[
                ...importResults.success.map((item: any) => ({ ...item, status: 'success' })),
                ...importResults.errors.map((item: any) => ({ ...item, status: 'error' }))
              ]}
              columns={resultColumns}
              rowKey="sku"
              size="small"
              pagination={false}
            />
          </>
        )}
      </Modal>
    </div>
  );
};

export default Products; 