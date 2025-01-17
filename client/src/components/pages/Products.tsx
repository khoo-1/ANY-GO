import React from 'react';
import { Card, Button, Modal, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import axios from 'axios';
import ProductForm from '../components/product/ProductForm';
import ProductList from '../components/inventory/ProductList';
import { Product } from '../types';

const Products = () => {
  const [modalVisible, setModalVisible] = React.useState(false);
  const [loading, setLoading] = React.useState(false);
  const [editingProduct, setEditingProduct] = React.useState<Product | null>(null);
  // ... 其余代码保持不变
}; 