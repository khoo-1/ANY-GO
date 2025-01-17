import React from 'react';
import { Layout, Menu } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  ShoppingOutlined,
  DatabaseOutlined,
  ShopOutlined,
  BarChartOutlined,
  SettingOutlined
} from '@ant-design/icons';
import Inventory from './pages/Inventory';
import Products from './pages/Products';
import 'antd/dist/antd.css';

const { Header, Sider, Content } = Layout;

const App = () => {
  const [collapsed, setCollapsed] = React.useState(false);
  const [selectedKey, setSelectedKey] = React.useState('inventory');

  const renderContent = () => {
    switch (selectedKey) {
      case 'inventory':
        return <Inventory />;
      case 'products':
        return <Products />;
      default:
        return <div>开发中...</div>;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div className="logo" style={{ height: 64, background: 'rgba(255,255,255,0.1)', margin: 16 }} />
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          onSelect={({ key }) => setSelectedKey(key)}
          items={[
            {
              key: 'orders',
              icon: <ShoppingOutlined />,
              label: '订单管理',
            },
            {
              key: 'inventory',
              icon: <DatabaseOutlined />,
              label: '库存管理',
            },
            {
              key: 'products',
              icon: <ShopOutlined />,
              label: '商品管理',
            },
            {
              key: 'statistics',
              icon: <BarChartOutlined />,
              label: '数据统计',
            },
            {
              key: 'settings',
              icon: <SettingOutlined />,
              label: '系统设置',
            },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: '#fff' }}>
          {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
            className: 'trigger',
            onClick: () => setCollapsed(!collapsed),
            style: { padding: '0 24px', fontSize: '18px' }
          })}
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  );
};

export default App; 