import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Products from './components/pages/Products';
import PackingLists from './components/pages/PackingLists';

const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Products />} />
        <Route path="packing-lists" element={<PackingLists />} />
      </Route>
    </Routes>
  );
};

export default App;
