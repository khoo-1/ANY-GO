import React from 'react';
import { Routes, Route, Navigate, BrowserRouter } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Products from './components/pages/Products';
import PackingLists from './components/pages/PackingLists';
import Login from './components/pages/Login';
import authService from './services/authService';
import { AuthProvider } from './contexts/AuthContext';

// 路由配置
const routerConfig = {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true
  }
};

// 路由保护组件
const PrivateRoute: React.FC<{ element: React.ReactElement }> = ({ element }) => {
  const isAuthenticated = authService.isAuthenticated();
  return isAuthenticated ? element : <Navigate to="/login" />;
};

const App: React.FC = () => {
  return (
    <BrowserRouter {...routerConfig}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<PrivateRoute element={<MainLayout />} />}>
            <Route index element={<Products />} />
            <Route path="products" element={<Products />} />
            <Route path="packing-lists" element={<PackingLists />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
