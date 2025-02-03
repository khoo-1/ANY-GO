import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import 'antd/dist/antd.css';
import './index.css';

// 添加 Router 配置
const routerConfig = {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true
  }
};

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter {...routerConfig}>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById('root')
);
