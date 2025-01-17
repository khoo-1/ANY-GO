import React from 'react';
import { Card, Tabs, Space, Button, Input, Select } from 'antd';
import { SearchOutlined, DownloadOutlined, UploadOutlined } from '@ant-design/icons';
import ProductList from '../components/inventory/ProductList';
import BatchOperations from '../components/product/BatchOperations';

const { TabPane } = Tabs;
const { Option } = Select;

const Inventory: React.FC = () => {
  return (
    <div>
      <Card>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Space wrap>
            <Input.Group compact>
              <Select defaultValue="sku" style={{ width: 120 }}>
                <Option value="sku">SKU</Option>
                <Option value="name">商品名称</Option>
                <Option value="supplier">供应商</Option>
              </Select>
              <Input 
                style={{ width: 200 }} 
                placeholder="请输入搜索内容"
                suffix={<SearchOutlined />}
              />
            </Input.Group>
            <Select style={{ width: 120 }} placeholder="库存状态">
              <Option value="normal">库存正常</Option>
              <Option value="low">库存不足</Option>
              <Option value="out">无库存</Option>
            </Select>
            <Button type="primary" icon={<SearchOutlined />}>搜索</Button>
            <Button icon={<DownloadOutlined />}>导出</Button>
            <Button icon={<UploadOutlined />}>导入</Button>
          </Space>

          <Tabs defaultActiveKey="all">
            <TabPane tab="全部商品" key="all">
              <ProductList />
            </TabPane>
            <TabPane tab="库存预警" key="warning">
              <ProductList lowStockOnly />
            </TabPane>
            <TabPane tab="无库存" key="outOfStock">
              <ProductList outOfStock />
            </TabPane>
          </Tabs>
        </Space>
      </Card>
    </div>
  );
};

export default Inventory; 