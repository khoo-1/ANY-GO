import React from 'react';
import {
  Table,
  Card,
  Button,
  Space,
  Tag,
  Modal,
  Select,
  message,
  Popconfirm
} from 'antd';
import {
  CloudUploadOutlined,
  CloudDownloadOutlined,
  DeleteOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import backupService, { BackupQuery } from '../../services/backupService';
import { Backup } from '../../types/api';
import dayjs from 'dayjs';

const { Option } = Select;

const Backups: React.FC = () => {
  const [backups, setBackups] = React.useState<Backup[]>([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(false);
  const [createModalVisible, setCreateModalVisible] = React.useState(false);
  const [selectedType, setSelectedType] = React.useState('full');
  const [query, setQuery] = React.useState<BackupQuery>({
    page: 1,
    pageSize: 10
  });

  const fetchBackups = async () => {
    try {
      setLoading(true);
      const response = await backupService.list(query);
      setBackups(response.items);
      setTotal(response.pagination.total);
    } catch (error) {
      console.error('获取备份列表失败:', error);
      message.error('获取备份列表失败');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchBackups();
  }, [query]);

  const handleCreate = async () => {
    try {
      await backupService.create(selectedType);
      message.success('创建备份任务成功');
      setCreateModalVisible(false);
      fetchBackups();
    } catch (error) {
      console.error('创建备份失败:', error);
      message.error('创建备份失败');
    }
  };

  const handleRestore = async (id: string) => {
    try {
      await backupService.restore(id);
      message.success('恢复备份成功');
    } catch (error) {
      console.error('恢复备份失败:', error);
      message.error('恢复备份失败');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await backupService.delete(id);
      message.success('删除备份成功');
      fetchBackups();
    } catch (error) {
      console.error('删除备份失败:', error);
      message.error('删除备份失败');
    }
  };

  const columns = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename'
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const colors: Record<string, string> = {
          full: 'blue',
          products: 'green',
          packingLists: 'orange'
        };
        const labels: Record<string, string> = {
          full: '全量备份',
          products: '商品数据',
          packingLists: '装箱单数据'
        };
        return <Tag color={colors[type]}>{labels[type]}</Tag>;
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors: Record<string, string> = {
          pending: 'processing',
          completed: 'success',
          failed: 'error'
        };
        const labels: Record<string, string> = {
          pending: '进行中',
          completed: '已完成',
          failed: '失败'
        };
        return <Tag color={colors[status]}>{labels[status]}</Tag>;
      }
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      render: (size: number) => {
        const units = ['B', 'KB', 'MB', 'GB'];
        let value = size;
        let unitIndex = 0;
        while (value >= 1024 && unitIndex < units.length - 1) {
          value /= 1024;
          unitIndex++;
        }
        return `${value.toFixed(2)} ${units[unitIndex]}`;
      }
    },
    {
      title: '创建者',
      dataIndex: ['createdBy', 'username'],
      key: 'createdBy'
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: '完成时间',
      dataIndex: 'completedAt',
      key: 'completedAt',
      render: (date: string) => date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Backup) => (
        <Space>
          {record.status === 'completed' && (
            <Popconfirm
              title="确定要恢复此备份吗？这将覆盖当前数据！"
              onConfirm={() => handleRestore(record._id)}
            >
              <Button
                type="link"
                icon={<CloudDownloadOutlined />}
              >
                恢复
              </Button>
            </Popconfirm>
          )}
          <Popconfirm
            title="确定要删除此备份吗？"
            onConfirm={() => handleDelete(record._id)}
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <Card>
      <Space style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<CloudUploadOutlined />}
          onClick={() => setCreateModalVisible(true)}
        >
          创建备份
        </Button>
        <Button
          icon={<ReloadOutlined />}
          onClick={() => fetchBackups()}
        >
          刷新
        </Button>
      </Space>

      <Table
        columns={columns}
        dataSource={backups}
        rowKey="_id"
        loading={loading}
        pagination={{
          total,
          current: query.page,
          pageSize: query.pageSize,
          onChange: (page, pageSize) => setQuery({ ...query, page, pageSize })
        }}
      />

      <Modal
        title="创建备份"
        open={createModalVisible}
        onOk={handleCreate}
        onCancel={() => setCreateModalVisible(false)}
      >
        <Select
          style={{ width: '100%' }}
          value={selectedType}
          onChange={setSelectedType}
        >
          <Option value="full">全量备份</Option>
          <Option value="products">仅商品数据</Option>
          <Option value="packingLists">仅装箱单数据</Option>
        </Select>
      </Modal>
    </Card>
  );
};

export default Backups; 