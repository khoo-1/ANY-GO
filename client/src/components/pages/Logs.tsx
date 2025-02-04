import React from 'react';
import {
  Table,
  Card,
  Space,
  Tag,
  DatePicker,
  Form,
  Select,
  Input,
  Button,
  Row,
  Col,
  Statistic
} from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import logService, { LogQuery } from '../../services/logService';
import { OperationLog } from '../../types/api';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

const Logs: React.FC = () => {
  const [logs, setLogs] = React.useState<OperationLog[]>([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(false);
  const [stats, setStats] = React.useState<any>(null);
  const [form] = Form.useForm();
  const [query, setQuery] = React.useState<LogQuery>({
    page: 1,
    pageSize: 10
  });

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await logService.list(query);
      setLogs(response.items);
      setTotal(response.pagination.total);
    } catch (error) {
      console.error('获取日志列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const { startDate, endDate } = query;
      const stats = await logService.getStatistics({ startDate, endDate });
      setStats(stats);
    } catch (error) {
      console.error('获取统计数据失败:', error);
    }
  };

  React.useEffect(() => {
    fetchLogs();
    fetchStats();
  }, [query]);

  const handleSearch = async (values: any) => {
    const { dateRange, ...rest } = values;
    const newQuery = {
      ...query,
      ...rest,
      page: 1,
      startDate: dateRange?.[0]?.format('YYYY-MM-DD'),
      endDate: dateRange?.[1]?.format('YYYY-MM-DD')
    };
    setQuery(newQuery);
  };

  const handleReset = () => {
    form.resetFields();
    setQuery({
      page: 1,
      pageSize: 10
    });
  };

  const columns = [
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username'
    },
    {
      title: '模块',
      dataIndex: 'module',
      key: 'module',
      render: (module: string) => {
        const colors: Record<string, string> = {
          products: 'blue',
          packingLists: 'green',
          users: 'purple',
          system: 'orange'
        };
        return <Tag color={colors[module]}>{module}</Tag>;
      }
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      render: (action: string) => {
        const colors: Record<string, string> = {
          create: 'success',
          update: 'processing',
          delete: 'error',
          read: 'default',
          import: 'warning',
          export: 'warning',
          backup: 'processing'
        };
        return <Tag color={colors[action]}>{action}</Tag>;
      }
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 300
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'success' ? 'success' : 'error'}>
          {status === 'success' ? '成功' : '失败'}
        </Tag>
      )
    },
    {
      title: 'IP地址',
      dataIndex: 'ip',
      key: 'ip'
    },
    {
      title: '时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')
    }
  ];

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="总操作次数"
              value={total}
            />
          </Col>
          {stats?.moduleStats?.map((stat: any) => (
            <Col span={6} key={stat._id}>
              <Statistic
                title={`${stat._id}模块操作`}
                value={stat.count}
              />
            </Col>
          ))}
        </Row>
      </Card>

      <Card>
        <Form
          form={form}
          layout="inline"
          onFinish={handleSearch}
          style={{ marginBottom: 16 }}
        >
          <Form.Item name="dateRange">
            <RangePicker />
          </Form.Item>
          <Form.Item name="module">
            <Select style={{ width: 120 }} placeholder="选择模块">
              <Option value="products">商品</Option>
              <Option value="packingLists">装箱单</Option>
              <Option value="users">用户</Option>
              <Option value="system">系统</Option>
            </Select>
          </Form.Item>
          <Form.Item name="action">
            <Select style={{ width: 120 }} placeholder="选择操作">
              <Option value="create">创建</Option>
              <Option value="update">更新</Option>
              <Option value="delete">删除</Option>
              <Option value="read">查看</Option>
              <Option value="import">导入</Option>
              <Option value="export">导出</Option>
              <Option value="backup">备份</Option>
            </Select>
          </Form.Item>
          <Form.Item name="username">
            <Input placeholder="用户名" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SearchOutlined />}
              >
                搜索
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReset}
              >
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>

        <Table
          columns={columns}
          dataSource={logs}
          rowKey="_id"
          loading={loading}
          pagination={{
            total,
            current: query.page,
            pageSize: query.pageSize,
            onChange: (page, pageSize) => setQuery({ ...query, page, pageSize })
          }}
        />
      </Card>
    </Space>
  );
};

export default Logs; 