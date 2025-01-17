import React from 'react';
import { Table, Tag } from 'antd';
import axios from 'axios';
import moment from 'moment';
import { StockRecord } from '../../types';

interface Props {
  productId: string;
}

const StockHistory = ({ productId }: Props) => {
  const [history, setHistory] = React.useState<StockRecord[]>([]);
  const [loading, setLoading] = React.useState(false);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:5000/api/inventory/history/${productId}`);
      setHistory(response.data);
    } catch (error) {
      console.error('获取历史记录失败:', error);
    }
    setLoading(false);
  };

  React.useEffect(() => {
    fetchHistory();
  }, [productId]);

  const columns = [
    {
      title: '时间',
      dataIndex: 'date',
      key: 'date',
      render: (date: string) => moment(date).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const color = type === '入库' ? 'success' : type === '出库' ? 'error' : 'warning';
        return <Tag color={color}>{type}</Tag>;
      },
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: '变更前库存',
      dataIndex: 'previousStock',
      key: 'previousStock',
    },
    {
      title: '变更后库存',
      dataIndex: 'currentStock',
      key: 'currentStock',
    },
    {
      title: '原因',
      dataIndex: 'reason',
      key: 'reason',
    },
    {
      title: '操作人',
      dataIndex: 'operator',
      key: 'operator',
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={history}
      rowKey="_id"
      loading={loading}
    />
  );
};

export default StockHistory; 