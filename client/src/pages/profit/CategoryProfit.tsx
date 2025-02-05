import React, { useState, useEffect } from 'react';
import { Card, Table, DatePicker, Select, Input, Form, Space, Button } from 'antd';
import type { TablePaginationConfig } from 'antd/lib/table';
import { SearchOutlined } from '@ant-design/icons';
import profitService, { CategoryProfit } from '../../services/profitService';
import { formatCurrency, formatPercent } from '../../utils/format';

const { RangePicker } = DatePicker;
const { Option } = Select;

const CategoryProfitPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<CategoryProfit[]>([]);
  const [pagination, setPagination] = useState<TablePaginationConfig>({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [form] = Form.useForm();

  // 加载数据
  const loadData = async (params: any = {}) => {
    try {
      setLoading(true);
      const { current, pageSize, ...filters } = params;
      const response = await profitService.getCategoryProfits({
        page: current || 1,
        page_size: pageSize || 10,
        ...filters
      });
      setData(response.items);
      setPagination({
        ...pagination,
        current: response.page,
        pageSize: response.page_size,
        total: response.total
      });
    } catch (error) {
      console.error('加载品类利润数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 处理表格变化
  const handleTableChange = (newPagination: TablePaginationConfig) => {
    const filters = form.getFieldsValue();
    loadData({
      current: newPagination.current,
      pageSize: newPagination.pageSize,
      ...filters
    });
  };

  // 处理搜索
  const handleSearch = () => {
    const values = form.getFieldsValue();
    loadData({
      current: 1,
      ...values
    });
  };

  // 处理重置
  const handleReset = () => {
    form.resetFields();
    loadData({
      current: 1
    });
  };

  const columns = [
    {
      title: '品类',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: '商品总数',
      dataIndex: 'totalProducts',
      key: 'totalProducts',
      sorter: true,
    },
    {
      title: '订单总数',
      dataIndex: 'totalOrders',
      key: 'totalOrders',
      sorter: true,
    },
    {
      title: '销售数量',
      dataIndex: 'salesQuantity',
      key: 'salesQuantity',
      sorter: true,
    },
    {
      title: '销售金额',
      dataIndex: 'salesAmount',
      key: 'salesAmount',
      render: (value: number) => formatCurrency(value),
      sorter: true,
    },
    {
      title: '商品成本',
      dataIndex: 'productCost',
      key: 'productCost',
      render: (value: number) => formatCurrency(value),
      sorter: true,
    },
    {
      title: '运输成本',
      dataIndex: 'shippingCost',
      key: 'shippingCost',
      render: (value: number) => formatCurrency(value),
    },
    {
      title: '运营成本',
      dataIndex: 'operationCost',
      key: 'operationCost',
      render: (value: number) => formatCurrency(value),
    },
    {
      title: '毛利润',
      dataIndex: 'grossProfit',
      key: 'grossProfit',
      render: (value: number) => formatCurrency(value),
      sorter: true,
    },
    {
      title: '净利润',
      dataIndex: 'netProfit',
      key: 'netProfit',
      render: (value: number) => formatCurrency(value),
      sorter: true,
    },
    {
      title: '毛利率',
      dataIndex: 'grossProfitRate',
      key: 'grossProfitRate',
      render: (value: number) => formatPercent(value),
      sorter: true,
    },
    {
      title: '净利率',
      dataIndex: 'netProfitRate',
      key: 'netProfitRate',
      render: (value: number) => formatPercent(value),
      sorter: true,
    },
    {
      title: '平均订单金额',
      dataIndex: 'averageOrderValue',
      key: 'averageOrderValue',
      render: (value: number) => formatCurrency(value),
      sorter: true,
    },
    {
      title: '平均订单利润',
      dataIndex: 'averageProfitPerOrder',
      key: 'averageProfitPerOrder',
      render: (value: number) => formatCurrency(value),
      sorter: true,
    }
  ];

  return (
    <div className="category-profit">
      <Card>
        <Form
          form={form}
          layout="inline"
          onFinish={handleSearch}
          style={{ marginBottom: 24 }}
        >
          <Form.Item name="category">
            <Input
              placeholder="搜索品类名称"
              prefix={<SearchOutlined />}
              allowClear
            />
          </Form.Item>
          <Form.Item name="type">
            <Select style={{ width: 120 }} placeholder="分析类型">
              <Option value="daily">日度分析</Option>
              <Option value="weekly">周度分析</Option>
              <Option value="monthly">月度分析</Option>
            </Select>
          </Form.Item>
          <Form.Item name="dateRange">
            <RangePicker />
          </Form.Item>
          <Form.Item name="profitRange">
            <Select style={{ width: 160 }} placeholder="利润率范围">
              <Option value="high">高利润率 (&gt;30%)</Option>
              <Option value="medium">中等利润率 (10-30%)</Option>
              <Option value="low">低利润率 (&lt;10%)</Option>
              <Option value="loss">亏损</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                搜索
              </Button>
              <Button onClick={handleReset}>重置</Button>
            </Space>
          </Form.Item>
        </Form>

        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          pagination={pagination}
          loading={loading}
          onChange={handleTableChange}
          scroll={{ x: 2000 }}
        />
      </Card>
    </div>
  );
};

export default CategoryProfitPage; 