import React from 'react';
import { Form, Input, InputNumber, Select, Modal, message, Upload } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { Product } from '../../types/api';
import { productService } from '../../services/productService';
import { handleError } from '../../utils/errorHandler';
import { AxiosError } from 'axios';
import { ApiResponse } from '../../types';

interface Props {
  visible: boolean;
  product: Product | null;
  onCancel: () => void;
  onSuccess: () => void;
}

const ProductForm: React.FC<Props> = ({ visible, product, onCancel, onSuccess }) => {
  const [form] = Form.useForm();
  const [fileList, setFileList] = React.useState<any[]>([]);

  React.useEffect(() => {
    if (visible && product) {
      form.setFieldsValue({
        ...product,
        images: undefined
      });
      setFileList(product.images?.map((url, index) => ({
        uid: `-${index}`,
        name: url.split('/').pop(),
        status: 'done',
        url
      })) || []);
    } else {
      form.resetFields();
      setFileList([]);
    }
  }, [visible, product, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (product) {
        await productService.update(product.id, values);
        message.success('更新成功');
      } else {
        await productService.create(values);
        message.success('创建成功');
      }
      onSuccess();
    } catch (error) {
      handleError(error as AxiosError<ApiResponse> | Error);
    }
  };

  const uploadProps = {
    listType: 'picture-card' as const,
    fileList,
    onChange: ({ fileList: newFileList }: any) => {
      setFileList(newFileList);
    },
    beforeUpload: (file: File) => {
      const isImage = file.type.startsWith('image/');
      if (!isImage) {
        message.error('只能上传图片文件！');
        return false;
      }
      return true;
    }
  };

  return (
    <Modal
      title={product ? '编辑商品' : '添加商品'}
      open={visible}
      onCancel={onCancel}
      onOk={handleSubmit}
      width={800}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={product || {
          type: '普货',
          status: 'active',
          category: '未分类'
        }}
      >
        <Form.Item
          name="sku"
          label="SKU"
          rules={[
            { required: true, message: '请输入SKU' },
            { pattern: /^[A-Za-z0-9]{6,20}$/, message: 'SKU必须是6-20位字母数字组合' }
          ]}
        >
          <Input disabled={!!product} placeholder="请输入SKU" />
        </Form.Item>

        <Form.Item
          name="name"
          label="商品名称"
          rules={[{ required: true, message: '请输入商品名称' }]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          name="chineseName"
          label="中文名称"
        >
          <Input placeholder="如不填写，将自动生成" />
        </Form.Item>

        <Form.Item
          name="type"
          label="商品类型"
          rules={[{ required: true, message: '请选择商品类型' }]}
        >
          <Select>
            <Select.Option value="普货">普货</Select.Option>
            <Select.Option value="纺织">纺织</Select.Option>
            <Select.Option value="混装">混装</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="category"
          label="类别"
        >
          <Input />
        </Form.Item>

        <Form.Item
          name="price"
          label="售价"
          rules={[{ required: true, message: '请输入售价' }]}
        >
          <InputNumber min={0} precision={2} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="cost"
          label="成本价"
        >
          <InputNumber min={0} precision={2} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="stock"
          label="库存"
          rules={[{ required: true, message: '请输入库存' }]}
        >
          <InputNumber min={0} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="status"
          label="状态"
          rules={[{ required: true, message: '请选择状态' }]}
        >
          <Select>
            <Select.Option value="active">上架</Select.Option>
            <Select.Option value="inactive">下架</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="description"
          label="描述"
        >
          <Input.TextArea rows={4} />
        </Form.Item>

        <Form.Item
          label="商品图片"
          name="images"
          valuePropName="fileList"
          getValueFromEvent={e => {
            if (Array.isArray(e)) {
              return e;
            }
            return e?.fileList;
          }}
        >
          <Upload {...uploadProps}>
            {fileList.length >= 5 ? null : (
              <div>
                <PlusOutlined />
                <div style={{ marginTop: 8 }}>上传图片</div>
              </div>
            )}
          </Upload>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default ProductForm; 