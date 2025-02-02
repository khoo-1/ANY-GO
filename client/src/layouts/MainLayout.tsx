import React, { useState, useEffect } from 'react';
import { Layout, Menu, Spin } from 'antd';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { ShopOutlined, GiftOutlined } from '@ant-design/icons';

const { Header, Content, Footer } = Layout;

const MainLayout: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    // 模拟检查后端服务状态
    const checkServerStatus = async () => {
      try {
        const response = await fetch('http://localhost:5000');
        if (response.ok) {
          setLoading(false);
        }
      } catch (error) {
        console.error('后端服务未启动:', error);
      }
    };

    checkServerStatus();
  }, []);

  if (loading) {
    return (
      <div style={{ 
        height: '100vh', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        flexDirection: 'column',
        gap: '20px'
      }}>
        <Spin size="large" />
        <div>正在连接服务器...</div>
      </div>
    );
  }

  return (
    <Layout className="min-h-screen">
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <div className="logo" />
        <Menu 
          theme="dark" 
          mode="horizontal" 
          selectedKeys={[location.pathname === '/' ? '1' : '2']}
        >
          <Menu.Item key="1" icon={<ShopOutlined />}>
            <Link to="/">商品管理</Link>
          </Menu.Item>
          <Menu.Item key="2" icon={<GiftOutlined />}>
            <Link to="/packing-lists">装箱单管理</Link>
          </Menu.Item>
        </Menu>
      </Header>
      <Content style={{ padding: '24px 50px' }}>
        <div style={{ background: '#fff', padding: 24, minHeight: 280 }}>
          <Outlet />
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>ANY-GO ©2024</Footer>
    </Layout>
  );
};

export default MainLayout; 