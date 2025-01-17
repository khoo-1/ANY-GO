import React from 'react';
import { Modal, Form, Input, Select, InputNumber, message } from 'antd';
import axios from 'axios';
import { Product } from '../../types';

interface Props {
  visible: boolean;
  product: Product;
  onClose: () => void;
  onSuccess: () => void;
}

const StockUpdateModal = ({ visible, product, onClose, onSuccess }: Props) => {
  const [form] = Form.useForm();

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      await axios.post('http://localhost:5000/api/inventory/update-stock', {
        productId: product._id,
        ...values,
      });
      message.success('库存更新成功');
      onSuccess();
    } catch (error) {
      message.error('库存更新失败');
    }
  };

  return (
    <Modal
      title="更新库存"
      visible={visible}
      onOk={handleSubmit}
      onCancel={onClose}
    >
      <Form form={form} layout="vertical">
        <Form.Item label="SKU" name="sku">
          <Input disabled value={product.sku} />
        </Form.Item>
        <Form.Item label="产品名称" name="name">
          <Input disabled value={product.name} />
        </Form.Item>
        <Form.Item
          label="操作类型"
          name="type"
          rules={[{ required: true, message: '请选择操作类型' }]}
        >
          <Select>
            <Select.Option value="入库">入库</Select.Option>
            <Select.Option value="出库">出库</Select.Option>
            <Select.Option value="调整">调整</Select.Option>
          </Select>
        </Form.Item>
        <Form.Item
          label="数量"
          name="quantity"
          rules={[{ required: true, message: '请输入数量' }]}
        >
          <InputNumber min={1} />
        </Form.Item>
        <Form.Item
          label="原因"
          name="reason"
          rules={[{ required: true, message: '请输入原因' }]}
        >
          <Input.TextArea />
        </Form.Item>
        <Form.Item
          label="操作人"
          name="operator"
          rules={[{ required: true, message: '请输入操作人' }]}
        >
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default StockUpdateModal; 