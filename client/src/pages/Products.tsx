import * as React from 'react';
const { useState } = React;
import { Card, Button, Modal, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import axios from 'axios';
import ProductForm from '../components/product/ProductForm';
import ProductList from '../components/inventory/ProductList';
import { Product } from '../types';
import BatchOperations from '../components/product/BatchOperations';

const Products: React.FC = () => {
  const [modalVisible, setModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  const handleAddProduct = async (formData: FormData) => {
    setLoading(true);
    try {
      await axios.post('http://localhost:5000/api/products', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      message.success('添加商品成功');
      setModalVisible(false);
      setEditingProduct(null);
    } catch (error) {
      message.error('添加商品失败');
    }
    setLoading(false);
  };

  const handleEditProduct = async (formData: FormData) => {
    if (!editingProduct) return;
    
    setLoading(true);
    try {
      await axios.put(`http://localhost:5000/api/products/${editingProduct._id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      message.success('更新商品成功');
      setModalVisible(false);
      setEditingProduct(null);
    } catch (error) {
      message.error('更新商品失败');
    }
    setLoading(false);
  };

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setModalVisible(true);
  };

  const handleModalClose = () => {
    setModalVisible(false);
    setEditingProduct(null);
  };

  return (
    <div>
      <Card
        title="商品管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            添加商品
          </Button>
        }
      >
        <BatchOperations onSuccess={() => {
          // 刷新商品列表
          const productListComponent = document.querySelector('ProductList');
          if (productListComponent) {
            productListComponent.dispatchEvent(new Event('refresh'));
          }
        }} />
        <ProductList onEdit={handleEdit} onRefresh={() => setModalVisible(false)} />
      </Card>

      <Modal
        title={editingProduct ? '编辑商品' : '添加商品'}
        open={modalVisible}
        onCancel={handleModalClose}
        footer={null}
        width={800}
        destroyOnClose
      >
        <ProductForm 
          initialValues={editingProduct}
          onFinish={editingProduct ? handleEditProduct : handleAddProduct}
          loading={loading}
        />
      </Modal>
    </div>
  );
};

export default Products; 