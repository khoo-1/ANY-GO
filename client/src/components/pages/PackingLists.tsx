import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { Table, Button, Space, message, Modal, Input, Select, Upload, DatePicker } from 'antd';
import { UploadOutlined, SearchOutlined, CheckCircleOutlined, DeleteOutlined } from '@ant-design/icons';
import { PackingList, PackingListQuery } from '../../types/api';
import { packingListService } from '../../services/packingListService';
import { handleError } from '../../utils/errorHandler';
import { AxiosError } from 'axios';
import { ApiResponse } from '../../types';
import dayjs from 'dayjs';

const { Search } = Input;
const { RangePicker } = DatePicker;

// 添加错误处理
const ignoreResizeObserverError = () => {
  const resizeObserverError = console.error;
  console.error = (...args: any) => {
    if (
      args.length > 0 &&
      typeof args[0] === 'string' &&
      args[0].includes('ResizeObserver')
    ) {
      return;
    }
    resizeObserverError.apply(console, args);
  };
};

// 将详情表格列配置提取出来
const detailColumns = [
  { title: '箱号', dataIndex: 'boxNo', key: 'boxNo', width: 100 },
  { title: 'SKU', dataIndex: 'sku', key: 'sku', width: 150 },
  { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 100 },
  { title: '重量', dataIndex: 'weight', key: 'weight', width: 100 },
  { title: '体积', dataIndex: 'volume', key: 'volume', width: 100 }
];

const PackingLists: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [packingLists, setPackingLists] = useState<PackingList[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState<PackingListQuery>({ page: 1, pageSize: 10 });
  const [importVisible, setImportVisible] = useState(false);
  const [selectedList, setSelectedList] = useState<PackingList | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const searchTimeoutRef = useRef<NodeJS.Timeout>();

  const loadPackingLists = useCallback(async () => {
    try {
      setLoading(true);
      const res = await packingListService.list(query);
      setPackingLists(res.data.items);
      setTotal(res.data.pagination.total);
    } catch (error) {
      handleError(error as AxiosError<ApiResponse> | Error);
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    loadPackingLists();
    ignoreResizeObserverError();
  }, [loadPackingLists]);

  const handleDelete = async (id: string) => {
    try {
      await packingListService.delete(id);
      message.success('删除成功');
      loadPackingLists();
    } catch (error) {
      handleError(error as AxiosError<ApiResponse> | Error);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await packingListService.updateStatus(id, 'approved');
      message.success('审核通过');
      loadPackingLists();
    } catch (error) {
      handleError(error as AxiosError<ApiResponse> | Error);
    }
  };

  // 使用 useMemo 缓存列配置
  const columns = useMemo(() => [
    {
      title: '店铺名称',
      dataIndex: 'storeName',
      key: 'storeName',
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
      onFilter: (value: any, record: PackingList) => record.type === value
    },
    {
      title: '总箱数',
      dataIndex: 'totalBoxes',
      key: 'totalBoxes',
      width: 100
    },
    {
      title: '总重量(kg)',
      dataIndex: 'totalWeight',
      key: 'totalWeight',
      width: 120
    },
    {
      title: '总体积(m³)',
      dataIndex: 'totalVolume',
      key: 'totalVolume',
      width: 120
    },
    {
      title: '总件数',
      dataIndex: 'totalPieces',
      key: 'totalPieces',
      width: 100
    },
    {
      title: '总金额',
      dataIndex: 'totalValue',
      key: 'totalValue',
      width: 120,
      render: (value: number) => `¥${value.toFixed(2)}`
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <span style={{ color: status === 'approved' ? '#52c41a' : '#faad14' }}>
          {status === 'approved' ? '已审核' : '待审核'}
        </span>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right' as const,
      width: 200,
      render: (_: unknown, record: PackingList) => (
        <Space>
          <Button
            type="link"
            onClick={() => {
              setSelectedList(record);
              setDetailVisible(true);
            }}
          >
            详情
          </Button>
          {record.status === 'pending' && (
            <>
              <Button
                type="link"
                icon={<CheckCircleOutlined />}
                onClick={() => {
                  Modal.confirm({
                    title: '确认审核',
                    content: '确定要审核通过这个装箱单吗？',
                    onOk: () => handleApprove(record.id)
                  });
                }}
              >
                审核
              </Button>
              <Button
                type="link"
                danger
                icon={<DeleteOutlined />}
                onClick={() => {
                  Modal.confirm({
                    title: '确认删除',
                    content: '确定要删除这个装箱单吗？',
                    onOk: () => handleDelete(record.id)
                  });
                }}
              >
                删除
              </Button>
            </>
          )}
        </Space>
      )
    }
  ], [handleDelete, handleApprove]);

  // 使用 useCallback 和 useRef 实现防抖
  const handleSearch = useCallback((value: string) => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    searchTimeoutRef.current = setTimeout(() => {
      setQuery(prev => ({ ...prev, page: 1, storeName: value }));
    }, 300);
  }, []);

  // 使用 useCallback 优化其他处理函数
  const handleTypeFilter = useCallback((value: PackingList['type'] | undefined) => {
    setQuery(prev => ({ ...prev, page: 1, type: value }));
  }, []);

  const handleDateRange = useCallback((dates: any) => {
    if (dates) {
      setQuery(prev => ({
        ...prev,
        page: 1,
        startDate: dates[0].format('YYYY-MM-DD'),
        endDate: dates[1].format('YYYY-MM-DD')
      }));
    } else {
      setQuery(prev => {
        const { startDate, endDate, ...rest } = prev;
        return { ...rest, page: 1 };
      });
    }
  }, []);

  const handleImport = async (file: File) => {
    try {
      const res = await packingListService.import(file);
      message.success(res.data.message);
      loadPackingLists();
      setImportVisible(false);
    } catch (error) {
      handleError(error as AxiosError<ApiResponse> | Error);
    }
  };

  return (
    <div style={{ 
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 200px)'  // 减去头部和底部的高度
    }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Button
            type="primary"
            icon={<UploadOutlined />}
            onClick={() => setImportVisible(true)}
          >
            导入装箱单
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
          <RangePicker onChange={handleDateRange} />
        </Space>
        <Search
          placeholder="搜索店铺名称"
          allowClear
          enterButton={<SearchOutlined />}
          onSearch={handleSearch}
          style={{ width: 300 }}
        />
      </div>

      <div style={{ flex: 1, overflow: 'hidden' }}>
        <Table
          loading={loading}
          columns={columns}
          dataSource={packingLists}
          rowKey="id"
          scroll={{ x: 1500, y: 'calc(100vh - 300px)' }}  // 动态计算表格高度
          pagination={{
            total,
            current: query.page,
            pageSize: query.pageSize,
            onChange: (page, pageSize) => setQuery(prev => ({ ...prev, page, pageSize })),
            showSizeChanger: false,
            position: ['bottomCenter']  // 固定分页器位置
          }}
          style={{ 
            height: '100%',
            overflow: 'hidden'
          }}
        />
      </div>

      <Modal
        title="导入装箱单"
        open={importVisible}
        onCancel={() => setImportVisible(false)}
        footer={null}
        destroyOnClose
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
            支持 .xlsx, .xls 格式的文件，文件名格式：店铺名海运ERP.xlsx
          </p>
        </Upload.Dragger>
      </Modal>

      {selectedList && (
        <Modal
          title="装箱单详情"
          open={detailVisible}
          onCancel={() => {
            setDetailVisible(false);
            setSelectedList(null);
          }}
          width={1000}
          footer={null}
          destroyOnClose
          style={{ top: 20 }}  // 调整模态框位置
        >
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
              <p><strong>店铺名称：</strong>{selectedList.storeName}</p>
              <p><strong>类型：</strong>{selectedList.type}</p>
              <p><strong>状态：</strong>{selectedList.status === 'approved' ? '已审核' : '待审核'}</p>
              <p><strong>总箱数：</strong>{selectedList.totalBoxes}</p>
              <p><strong>总重量：</strong>{selectedList.totalWeight}kg</p>
              <p><strong>总体积：</strong>{selectedList.totalVolume}m³</p>
              <p><strong>总件数：</strong>{selectedList.totalPieces}</p>
              <p><strong>总金额：</strong>¥{selectedList.totalValue.toFixed(2)}</p>
            </div>
          </div>
          <Table
            columns={detailColumns}
            dataSource={selectedList.items}
            rowKey={(record) => `${record.boxNo}-${record.sku}`}
            pagination={false}
            scroll={{ y: 'calc(100vh - 500px)' }}  // 动态计算详情表格高度
            size="small"
            style={{ 
              overflow: 'hidden',
              marginTop: 16
            }}
          />
        </Modal>
      )}
    </div>
  );
};

export default React.memo(PackingLists); 