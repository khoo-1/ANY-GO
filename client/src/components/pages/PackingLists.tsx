import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { Table, Button, Space, message, Modal, Input, Select, Upload, DatePicker, Tabs, Divider, Checkbox, Radio, Form } from 'antd';
import { UploadOutlined, SearchOutlined, CheckCircleOutlined, DeleteOutlined, DownloadOutlined, PrinterOutlined } from '@ant-design/icons';
import { PackingList, PackingListQuery } from '../../types/api';
import { packingListService } from '../../services/packingListService';
import { handleError } from '../../utils/errorHandler';
import { AxiosError } from 'axios';
import { ApiResponse } from '../../types';
import dayjs from 'dayjs';
import type { RadioChangeEvent } from 'antd/es/radio';
import type { CheckboxValueType } from 'antd/es/checkbox/Group';

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
  { 
    title: '箱号',
    dataIndex: 'boxNo',
    key: 'boxNo',
    width: 80,
    fixed: 'left' as const
  },
  { 
    title: 'SKU',
    dataIndex: 'sku',
    key: 'sku',
    width: 150,
    fixed: 'left' as const
  },
  { 
    title: '中文名',
    dataIndex: 'chineseName',
    key: 'chineseName',
    width: 200
  },
  { 
    title: '数量',
    dataIndex: 'quantity',
    key: 'quantity',
    width: 80
  },
  {
    title: '箱规格',
    children: [
      { 
        title: '长(cm)',
        dataIndex: ['specs', 'length'],
        key: 'length',
        width: 80
      },
      { 
        title: '宽(cm)',
        dataIndex: ['specs', 'width'],
        key: 'width',
        width: 80
      },
      { 
        title: '高(cm)',
        dataIndex: ['specs', 'height'],
        key: 'height',
        width: 80
      }
    ]
  },
  { 
    title: '重量(kg)',
    dataIndex: ['specs', 'weight'],
    key: 'weight',
    width: 100
  },
  { 
    title: '体积(m³)',
    dataIndex: ['specs', 'volume'],
    key: 'volume',
    width: 100
  },
  { 
    title: '单边+1(m³)',
    dataIndex: ['specs', 'edgeVolume'],
    key: 'edgeVolume',
    width: 100
  }
];

// 添加打印样式组件
const PrintStyles = () => (
  <style>
    {`
      @media print {
        body * {
          visibility: hidden;
        }
        .print-content, .print-content * {
          visibility: visible;
        }
        .print-content {
          position: absolute;
          left: 0;
          top: 0;
          width: 100%;
        }
        .no-print {
          display: none !important;
        }
      }
    `}
  </style>
);

// 打印选项组件
const PrintOptions: React.FC<{
  onChange: (options: PrintSettings) => void;
  defaultOptions?: PrintSettings;
}> = ({ onChange, defaultOptions }) => {
  const [options, setOptions] = useState<PrintSettings>(defaultOptions || {
    printMode: 'detailed',
    sections: ['header', 'summary', 'items'],
    paperSize: 'A4',
  });

  const handleModeChange = (e: RadioChangeEvent) => {
    const newOptions = { ...options, printMode: e.target.value };
    setOptions(newOptions);
    onChange(newOptions);
  };

  const handleSectionsChange = (checkedValues: CheckboxValueType[]) => {
    const newOptions = { ...options, sections: checkedValues as string[] };
    setOptions(newOptions);
    onChange(newOptions);
  };

  const handlePaperSizeChange = (e: RadioChangeEvent) => {
    const newOptions = { ...options, paperSize: e.target.value };
    setOptions(newOptions);
    onChange(newOptions);
  };

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ marginBottom: 8 }}>
        <div style={{ marginBottom: 4 }}>打印模式：</div>
        <Radio.Group value={options.printMode} onChange={handleModeChange}>
          <Radio value="detailed">详细模式</Radio>
          <Radio value="simple">简单模式</Radio>
        </Radio.Group>
      </div>
      <div style={{ marginBottom: 8 }}>
        <div style={{ marginBottom: 4 }}>打印内容：</div>
        <Checkbox.Group value={options.sections} onChange={handleSectionsChange}>
          <Checkbox value="header">表头信息</Checkbox>
          <Checkbox value="summary">汇总信息</Checkbox>
          <Checkbox value="items">商品明细</Checkbox>
        </Checkbox.Group>
      </div>
      <div>
        <div style={{ marginBottom: 4 }}>纸张大小：</div>
        <Radio.Group value={options.paperSize} onChange={handlePaperSizeChange}>
          <Radio value="A4">A4</Radio>
          <Radio value="A5">A5</Radio>
          <Radio value="letter">Letter</Radio>
        </Radio.Group>
      </div>
    </div>
  );
};

// 修改打印预览组件
const PrintPreview: React.FC<{
  packingList: PackingList;
  onClose: () => void;
  printSettings?: PrintSettings;
}> = ({ packingList, onClose, printSettings = { printMode: 'detailed', sections: ['header', 'summary', 'items'], paperSize: 'A4' } }) => {
  const [options, setOptions] = useState(printSettings);
  const handlePrint = useCallback(() => {
    window.print();
  }, []);

  // 按箱号分组数据
  const groupedItems = useMemo(() => {
    const groups: { [key: string]: any[] } = {};
    packingList.items.forEach(item => {
      item.boxQuantities.forEach(bq => {
        if (!groups[bq.boxNo]) {
          groups[bq.boxNo] = [];
        }
        groups[bq.boxNo].push({
          ...item,
          quantity: bq.quantity,
          specs: bq.specs,
          boxNo: bq.boxNo
        });
      });
    });
    return groups;
  }, [packingList.items]);

  return (
    <Modal
      title="打印预览"
      open={true}
      onCancel={onClose}
      width={1200}
      footer={[
        <Button key="cancel" onClick={onClose}>取消</Button>,
        <Button key="print" type="primary" icon={<PrinterOutlined />} onClick={handlePrint}>打印</Button>
      ]}
      style={{ top: 20 }}
    >
      <PrintStyles />
      <PrintOptions onChange={setOptions} defaultOptions={options} />
      <div className="print-content" style={{ 
        width: options.paperSize === 'A4' ? '210mm' : options.paperSize === 'A5' ? '148mm' : '216mm',
        margin: '0 auto',
        background: '#fff',
        padding: '20mm',
        boxShadow: '0 0 10px rgba(0,0,0,0.1)'
      }}>
        {options.sections.includes('header') && (
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <h1>{packingList.storeName} - 装箱单</h1>
            <p>创建时间：{dayjs(packingList.createdAt).format('YYYY-MM-DD HH:mm:ss')}</p>
          </div>
        )}

        {options.sections.includes('summary') && (
          <div style={{ marginBottom: 24 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
              <div>
                <div>店铺：{packingList.storeName}</div>
                <div>类型：{packingList.type}</div>
              </div>
              <div>
                <div>总箱数：{packingList.totalBoxes} 箱</div>
                <div>总重量：{packingList.totalWeight.toFixed(2)} kg</div>
                <div>总体积：{packingList.totalVolume.toFixed(3)} m³</div>
              </div>
            </div>
          </div>
        )}

        {options.sections.includes('items') && (
          <>
            {Object.entries(groupedItems).map(([boxNo, items]) => (
              <div key={boxNo} style={{ marginBottom: 24, pageBreakInside: 'avoid' }}>
                <h2>箱号：{boxNo}</h2>
                {options.printMode === 'detailed' ? (
                  <>
                    <div style={{ marginBottom: 8 }}>
                      <Space>
                        <span>规格：{items[0].specs.length} × {items[0].specs.width} × {items[0].specs.height} cm</span>
                        <Divider type="vertical" />
                        <span>重量：{items[0].specs.weight.toFixed(2)} kg</span>
                        <Divider type="vertical" />
                        <span>体积：{items[0].specs.volume.toFixed(3)} m³</span>
                      </Space>
                    </div>
                    <Table
                      columns={[
                        { title: 'SKU', dataIndex: 'sku', width: 150 },
                        { title: '中文名', dataIndex: 'chineseName', width: 200 },
                        { title: '数量', dataIndex: 'quantity', width: 100 },
                        { title: '重量', dataIndex: ['specs', 'weight'], width: 100 },
                        { title: '体积', dataIndex: ['specs', 'volume'], width: 100 }
                      ]}
                      dataSource={items}
                      pagination={false}
                      size="small"
                      rowKey={(record) => `${record.boxNo}-${record.sku}-${record.quantity}`}
                    />
                  </>
                ) : (
                  <Table
                    columns={[
                      { title: 'SKU', dataIndex: 'sku', width: 150 },
                      { title: '数量', dataIndex: 'quantity', width: 100 }
                    ]}
                    dataSource={items}
                    pagination={false}
                    size="small"
                    rowKey={(record) => `${record.boxNo}-${record.sku}-${record.quantity}`}
                  />
                )}
              </div>
            ))}
          </>
        )}

        <div style={{ marginTop: 24 }}>
          <div>备注：{packingList.remarks || '无'}</div>
        </div>
      </div>
    </Modal>
  );
};

// 添加批量打印组件
const BatchPrintPreview: React.FC<{
  packingLists: PackingList[];
  onClose: () => void;
}> = ({ packingLists, onClose }) => {
  const [options, setOptions] = useState<PrintSettings>({
    printMode: 'simple',
    sections: ['header', 'items'],
    paperSize: 'A4'
  });

  return (
    <Modal
      title="批量打印预览"
      open={true}
      onCancel={onClose}
      width={1200}
      footer={[
        <Button key="cancel" onClick={onClose}>取消</Button>,
        <Button key="print" type="primary" icon={<PrinterOutlined />} onClick={() => window.print()}>
          打印
        </Button>
      ]}
      style={{ top: 20 }}
    >
      <PrintStyles />
      <PrintOptions onChange={setOptions} defaultOptions={options} />
      <div className="print-content">
        {packingLists.map((list, index) => (
          <div key={list._id} style={{ pageBreakBefore: index > 0 ? 'always' : 'auto' }}>
            <PrintPreview
              packingList={list}
              onClose={() => {}}
              printSettings={options}
            />
          </div>
        ))}
      </div>
    </Modal>
  );
};

// 创建装箱单详情组件
const PackingListDetail: React.FC<{
  packingList: PackingList;
  onClose: () => void;
}> = ({ packingList, onClose }) => {
  const [printVisible, setPrintVisible] = useState(false);

  // 按箱号分组数据
  const groupedItems = useMemo(() => {
    const groups: { [key: string]: any[] } = {};
    packingList.items.forEach(item => {
      item.boxQuantities.forEach(bq => {
        if (!groups[bq.boxNo]) {
          groups[bq.boxNo] = [];
        }
        groups[bq.boxNo].push({
          ...item,
          quantity: bq.quantity,
          specs: bq.specs,
          boxNo: bq.boxNo
        });
      });
    });
    return groups;
  }, [packingList.items]);

  // 计算每个箱子的合计
  const boxSummaries = useMemo(() => {
    const summaries: { [key: string]: { totalQuantity: number; totalWeight: number; totalVolume: number } } = {};
    Object.entries(groupedItems).forEach(([boxNo, items]) => {
      summaries[boxNo] = items.reduce((acc, item) => ({
        totalQuantity: acc.totalQuantity + item.quantity,
        totalWeight: acc.totalWeight + (item.specs.weight || 0),
        totalVolume: acc.totalVolume + (item.specs.volume || 0)
      }), { totalQuantity: 0, totalWeight: 0, totalVolume: 0 });
    });
    return summaries;
  }, [groupedItems]);

  return (
    <Modal
      title={`装箱单详情 - ${packingList.storeName}`}
      open={true}
      onCancel={onClose}
      width={1200}
      footer={[
        <Button key="print" icon={<PrinterOutlined />} onClick={() => setPrintVisible(true)}>
          打印预览
        </Button>,
        <Button key="close" onClick={onClose}>
          关闭
        </Button>
      ]}
      style={{ top: 20 }}
    >
      <div style={{ marginBottom: 24 }}>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(3, 1fr)', 
          gap: '16px',
          padding: '16px',
          background: '#f5f5f5',
          borderRadius: '8px'
        }}>
          <div>
            <div style={{ fontWeight: 'bold', marginBottom: 4 }}>基本信息</div>
            <div>店铺：{packingList.storeName}</div>
            <div>类型：{packingList.type}</div>
          </div>
          <div>
            <div style={{ fontWeight: 'bold', marginBottom: 4 }}>箱数信息</div>
            <div>总箱数：{packingList.totalBoxes} 箱</div>
            <div>总件数：{packingList.totalPieces} 件</div>
          </div>
          <div>
            <div style={{ fontWeight: 'bold', marginBottom: 4 }}>重量体积</div>
            <div>总重量：{packingList.totalWeight.toFixed(2)} kg</div>
            <div>总体积：{packingList.totalVolume.toFixed(3)} m³</div>
          </div>
        </div>
      </div>

      <Tabs
        type="card"
        items={Object.entries(groupedItems).map(([boxNo, items]) => ({
          label: `${boxNo}号箱`,
          key: boxNo,
          children: (
            <>
              <Table
                columns={detailColumns}
                dataSource={items}
                rowKey={(record) => `${record.boxNo}-${record.sku}-${record.quantity}`}
                pagination={false}
                scroll={{ x: 1100, y: 400 }}
                size="small"
                summary={() => (
                  <Table.Summary fixed="bottom">
                    <Table.Summary.Row>
                      <Table.Summary.Cell index={0} colSpan={3} align="right">
                        <strong>箱子合计：</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={3}>
                        <strong>{boxSummaries[boxNo].totalQuantity}</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={4} colSpan={3} />
                      <Table.Summary.Cell index={7}>
                        <strong>{boxSummaries[boxNo].totalWeight.toFixed(2)}</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={8}>
                        <strong>{boxSummaries[boxNo].totalVolume.toFixed(3)}</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={9} />
                    </Table.Summary.Row>
                  </Table.Summary>
                )}
              />
              <div style={{ marginTop: 16, textAlign: 'right' }}>
                <Space>
                  <span>箱子规格：{items[0].specs.length} × {items[0].specs.width} × {items[0].specs.height} cm</span>
                  <Divider type="vertical" />
                  <span>箱重：{items[0].specs.weight.toFixed(2)} kg</span>
                  <Divider type="vertical" />
                  <span>体积：{items[0].specs.volume.toFixed(3)} m³</span>
                  <Divider type="vertical" />
                  <span>单边+1：{items[0].specs.edgeVolume.toFixed(3)} m³</span>
                </Space>
              </div>
            </>
          )
        }))}
      />
      {printVisible && (
        <PrintPreview
          packingList={packingList}
          onClose={() => setPrintVisible(false)}
        />
      )}
    </Modal>
  );
};

const PackingLists: React.FC = () => {
  const [form] = Form.useForm();
  
  useEffect(() => {
    ignoreResizeObserverError();
  }, []);

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
      console.log('开始加载装箱单列表，参数:', query);
      const data = await packingListService.list(query);
      console.log('获取到的响应数据:', data);
      
      if (data?.items && Array.isArray(data.items)) {
        // 处理数据，确保所有必要字段都有值
        const processedItems = data.items.map(item => ({
          ...item,
          storeName: item.storeName || '未知店铺',
          type: item.type || '普货',
          totalBoxes: item.totalBoxes || 0,
          totalWeight: item.totalWeight || 0,
          totalVolume: item.totalVolume || 0,
          totalPieces: item.totalPieces || 0,
          createdAt: item.createdAt || new Date().toISOString()
        }));
        
        console.log('处理后的数据:', processedItems);
        setPackingLists(processedItems);
        setTotal(data.pagination.total);
      } else {
        console.error('返回数据格式不正确:', data);
        message.error('获取列表失败：返回数据格式不正确');
      }
    } catch (error) {
      console.error('加载装箱单列表出错:', error);
      handleError(error as AxiosError<ApiResponse> | Error);
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    loadPackingLists();
  }, [loadPackingLists]);

  const handleDelete = useCallback(async (id: string) => {
    if (!id) {
      message.error('ID不能为空');
      return;
    }
    console.log('准备删除装箱单，ID:', id);

    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个装箱单吗？',
      okText: '确定删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          console.log('开始删除装箱单，ID:', id);
          const response = await packingListService.delete(id);
          console.log('删除响应:', response);
          message.success('删除成功');
          loadPackingLists();
        } catch (error: any) {
          console.error('删除装箱单出错:', error);
          if (error.message?.includes('无效的ID格式')) {
            message.error('无效的ID格式，请检查ID是否正确');
          } else if (error.response?.status === 404) {
            message.error('装箱单不存在或已被删除');
          } else if (error.response?.status === 400) {
            message.error('无效的请求参数');
          } else if (error.response?.status === 500) {
            message.error('服务器错误，请稍后重试');
          } else {
            message.error('删除失败，请稍后重试');
          }
        }
      }
    });
  }, [loadPackingLists]);

  const handleExport = useCallback(async (id: string) => {
    if (!id) {
      message.error('ID不能为空');
      return;
    }
    try {
      await packingListService.export(id);
      message.success('导出成功');
    } catch (error: any) {
      if (error.message?.includes('无效的ID格式')) {
        message.error('无效的ID格式，请检查ID是否正确');
      } else if (error.response?.status === 404) {
        message.error('装箱单不存在或已被删除');
      } else {
        message.error('导出失败，请稍后重试');
      }
      console.error('导出装箱单时出错:', error);
    }
  }, []);

  const handleDeleteAll = useCallback(async () => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除所有装箱单吗？此操作不可恢复！',
      okText: '确定删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await packingListService.deleteAll();
          message.success('删除成功');
          loadPackingLists();
        } catch (error) {
          handleError(error as AxiosError<ApiResponse> | Error);
        }
      }
    });
  }, [loadPackingLists]);

  const columns = useMemo(() => [
    {
      title: '店铺名称',
      dataIndex: 'storeName',
      width: 200,
      render: (text: string) => text || '未知店铺'
    },
    {
      title: '类型',
      dataIndex: 'type',
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
      width: 100
    },
    {
      title: '总重量(kg)',
      dataIndex: 'totalWeight',
      width: 120,
      render: (val: number) => val.toFixed(2)
    },
    {
      title: '总体积(m³)',
      dataIndex: 'totalVolume',
      width: 120,
      render: (val: number) => val.toFixed(3)
    },
    {
      title: '总件数',
      dataIndex: 'totalPieces',
      width: 100
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: '操作',
      fixed: 'right' as const,
      width: 200,
      render: (_: any, record: PackingList) => (
        <Space size="middle">
          <Button
            type="link"
            onClick={() => {
              if (record._id) {
                setSelectedList(record);
                setDetailVisible(true);
              } else {
                message.error('记录ID不存在');
              }
            }}
          >
            查看
          </Button>
          <Button
            type="link"
            onClick={() => record._id ? handleExport(record._id) : message.error('记录ID不存在')}
          >
            导出
          </Button>
          <Button 
            type="link" 
            danger 
            onClick={() => record._id ? handleDelete(record._id) : message.error('记录ID不存在')}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ], [handleDelete, handleExport]);

  const handleSearch = useCallback((value: string) => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    searchTimeoutRef.current = setTimeout(() => {
      setQuery(prev => ({ ...prev, page: 1, storeName: value }));
    }, 300);
  }, []);

  const handleTypeFilter = useCallback((value: PackingList['type'] | undefined) => {
    setQuery(prev => ({ ...prev, page: 1, type: value }));
  }, []);

  const handleImport = async (file: File) => {
    try {
      const response = await packingListService.import(file);
      console.log('导入响应:', response);
      
      if (response && response.message) {
        message.success(response.message);
        // 重置查询参数并刷新列表
        setQuery({ page: 1, pageSize: 10 });
        await loadPackingLists();
        setImportVisible(false);
      } else {
        message.error('导入失败：服务器响应格式不正确');
      }
    } catch (error: any) {
      console.error('导入失败:', error);
      let errorMessage = '导入失败';
      
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }

      message.error(errorMessage);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Form form={form}>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <Space>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => setImportVisible(true)}
            >
              导入装箱单
            </Button>
            <Button
              danger
              type="primary"
              onClick={handleDeleteAll}
            >
              删除所有数据
            </Button>
            <Form.Item name="type" noStyle>
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
            </Form.Item>
          </Space>
          <Form.Item name="search" noStyle>
            <Search
              placeholder="搜索店铺名称"
              allowClear
              onSearch={handleSearch}
              style={{ width: 200 }}
            />
          </Form.Item>
        </div>
      </Form>

      <Table
        loading={loading}
        columns={columns}
        dataSource={packingLists}
        rowKey="_id"
        scroll={{ x: 1200 }}
        pagination={{
          total,
          current: query.page,
          pageSize: query.pageSize,
          onChange: (page, pageSize) => setQuery(prev => ({ ...prev, page, pageSize })),
          showSizeChanger: false
        }}
      />

      <Modal
        title="导入装箱单"
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

      {selectedList && detailVisible && (
        <PackingListDetail
          packingList={selectedList}
          onClose={() => {
            setDetailVisible(false);
            setSelectedList(null);
          }}
        />
      )}
    </div>
  );
};

// 添加类型定义
interface PrintSettings {
  printMode: 'detailed' | 'simple';
  sections: string[];
  paperSize: 'A4' | 'A5' | 'letter';
}

export default React.memo(PackingLists); 