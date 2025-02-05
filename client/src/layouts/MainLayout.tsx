import React, { useState, useEffect } from 'react';
import { Layout, Menu, Spin, Dropdown, Space } from 'antd';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { ShoppingOutlined, UnorderedListOutlined, UserOutlined, LogoutOutlined } from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';

const { Header, Content, Footer } = Layout;

const menuItems = [
  {
    key: '1',
    icon: <ShoppingOutlined />,
    label: <Link to="/products">商品管理</Link>
  },
  {
    key: '2',
    icon: <UnorderedListOutlined />,
    label: <Link to="/packing-lists">装箱单管理</Link>
  }
];

const MainLayout: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const selectedKey = location.pathname === '/products' || location.pathname === '/' ? '1' : '2';

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息'
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录'
    }
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      logout();
      navigate('/login');
    }
  };

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
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div className="logo" />
          <Menu 
            theme="dark" 
            mode="horizontal" 
            selectedKeys={[selectedKey]}
            items={menuItems}
          />
        </div>
        <div style={{ marginRight: '20px' }}>
          <Dropdown menu={{ items: userMenuItems, onClick: handleMenuClick }} placement="bottomRight">
            <Space style={{ color: '#fff', cursor: 'pointer' }}>
              <UserOutlined />
              {user?.username}
            </Space>
          </Dropdown>
        </div>
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