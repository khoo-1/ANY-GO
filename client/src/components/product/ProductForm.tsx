import React from 'react';
import { Form, Input, InputNumber, Select, Upload, Modal, Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import { Product } from '../../types';

const { TextArea } = Input;
const { Option } = Select;

interface ProductFormProps {
  initialValues?: Partial<Product>;
  onFinish: (values: FormData) => Promise<void>;
  loading?: boolean;
}

const ProductForm = ({ initialValues, onFinish, loading }: ProductFormProps) => {
  const [form] = Form.useForm();
  const [previewOpen, setPreviewOpen] = React.useState(false);
  const [previewImage, setPreviewImage] = React.useState('');
  const [fileList, setFileList] = React.useState<UploadFile[]>(() => {
    // 如果有初始图片，转换为 UploadFile 格式
    return initialValues?.images?.map((url, index) => ({
      uid: `-${index}`,
      name: url.split('/').pop() || 'image',
      status: 'done',
      url: `http://localhost:5000${url}`,
    })) || [];
  });

  // 当 initialValues 变化时重置表单
  React.useEffect(() => {
    if (initialValues) {
      form.setFieldsValue(initialValues);
    } else {
      form.resetFields();
    }
  }, [initialValues, form]);

  const handlePreview = async (file: UploadFile) => {
    setPreviewImage(file.url || (file.preview as string));
    setPreviewOpen(true);
  };

  const handleSubmit = async (values: any) => {
    const formData = new FormData();
    
    // 添加基本字段
    Object.keys(values).forEach(key => {
      if (key !== 'images') {
        formData.append(key, values[key]);
      }
    });

    // 添加图片文件
    fileList.forEach(file => {
      if (file.originFileObj) {
        formData.append('images', file.originFileObj);
      }
    });

    onFinish(formData);
  };

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={initialValues}
      onFinish={handleSubmit}
    >
      <Form.Item
        label="SKU"
        name="sku"
        rules={[{ required: true, message: '请输入SKU' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        label="商品名称"
        name="name"
        rules={[{ required: true, message: '请输入商品名称' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        label="商品图片"
        name="images"
        valuePropName="fileList"
        getValueFromEvent={(e) => {
          if (Array.isArray(e)) {
            return e;
          }
          return e?.fileList;
        }}
      >
        <Upload
          listType="picture-card"
          fileList={fileList}
          onPreview={handlePreview}
          onChange={({ fileList }) => setFileList(fileList)}
          beforeUpload={() => false}
        >
          {fileList.length >= 5 ? null : (
            <div>
              <PlusOutlined />
              <div style={{ marginTop: 8 }}>上传</div>
            </div>
          )}
        </Upload>
      </Form.Item>

      <Form.Item
        label="商品描述"
        name="description"
      >
        <TextArea rows={4} />
      </Form.Item>

      <Form.Item
        label="类别"
        name="category"
      >
        <Select>
          <Option value="clothing">服装</Option>
          <Option value="electronics">电子产品</Option>
          <Option value="home">家居用品</Option>
        </Select>
      </Form.Item>

      <Form.Item
        label="售价"
        name="price"
        rules={[{ required: true, message: '请输入售价' }]}
      >
        <InputNumber
          min={0}
          precision={2}
          style={{ width: '100%' }}
          prefix="￥"
        />
      </Form.Item>

      <Form.Item
        label="成本价"
        name="cost"
      >
        <InputNumber
          min={0}
          precision={2}
          style={{ width: '100%' }}
          prefix="￥"
        />
      </Form.Item>

      <Form.Item
        label="库存预警阈值"
        name="alertThreshold"
      >
        <InputNumber min={0} style={{ width: '100%' }} />
      </Form.Item>

      <Form.Item
        label="供应商"
        name="supplier"
      >
        <Input />
      </Form.Item>

      <Modal
        open={previewOpen}
        title="图片预览"
        footer={null}
        onCancel={() => setPreviewOpen(false)}
      >
        <img alt="preview" style={{ width: '100%' }} src={previewImage} />
      </Modal>

      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block>
          保存
        </Button>
      </Form.Item>
    </Form>
  );
};

export default ProductForm; 