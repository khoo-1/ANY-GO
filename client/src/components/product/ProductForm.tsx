import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Input, 
  InputNumber, 
  Select, 
  Modal, 
  message, 
  Upload,
  Row,
  Col,
  Divider,
  Space,
  Alert,
  Tooltip
} from 'antd';
import { 
  PlusOutlined, 
  QuestionCircleOutlined,
  LoadingOutlined 
} from '@ant-design/icons';
import { Product } from '../../types/api';
import productService from '../../services/productService';
import { handleError } from '../../utils/errorHandler';
import { AxiosError } from 'axios';
import { ApiResponse } from '../../types';
import type { UploadFile, RcFile } from 'antd/es/upload/interface';

interface ProductFormProps {
  visible: boolean;
  product: Product | null;
  onCancel: () => void;
  onSuccess: () => void;
}

const ProductForm: React.FC<ProductFormProps> = ({
  visible,
  product,
  onCancel,
  onSuccess
}) => {
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const isEdit = !!product;

  // 计算总成本
  const calculateTotalCost = () => {
    const cost = form.getFieldValue('cost') || 0;
    const freightCost = form.getFieldValue('freightCost') || 0;
    return (cost + freightCost).toFixed(2);
  };

  const onFinish = async (values: Partial<Product>) => {
    try {
      setSubmitLoading(true);

      // 处理图片上传
      if (fileList.length > 0) {
        values.images = fileList
          .filter(file => file.status === 'done' && file.url)
          .map(file => file.url as string);
      }

      if (isEdit && product) {
        await productService.update(product._id, values);
        message.success('更新成功');
      } else {
        await productService.create(values);
        message.success('创建成功');
      }
      onSuccess();
    } catch (error) {
      handleError(error as AxiosError);
    } finally {
      setSubmitLoading(false);
    }
  };

  useEffect(() => {
    if (visible && product) {
      form.setFieldsValue({
        ...product,
        images: undefined
      });
      setFileList(product.images?.map((url, index) => ({
        uid: `-${index}`,
        name: url.split('/').pop() || '',
        status: 'done',
        url
      })) || []);
    } else {
      form.resetFields();
      setFileList([]);
    }
  }, [visible, product, form]);

  const beforeUpload = (file: RcFile) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件！');
      return false;
    }
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error('图片大小不能超过 2MB！');
      return false;
    }
    return true;
  };

  const uploadProps = {
    listType: 'picture-card' as const,
    fileList,
    beforeUpload,
    onChange: ({ fileList: newFileList }: any) => {
      setFileList(newFileList);
    },
    onPreview: async (file: UploadFile) => {
      if (!file.url && !file.preview) {
        file.preview = await new Promise(resolve => {
          const reader = new FileReader();
          reader.readAsDataURL(file.originFileObj as Blob);
          reader.onload = () => resolve(reader.result as string);
        });
      }
      const image = new Image();
      image.src = file.url || file.preview || '';
      const imgWindow = window.open(file.url || file.preview);
      imgWindow?.document.write(image.outerHTML);
    }
  };

  return (
    <Modal
      title={isEdit ? '编辑商品' : '添加商品'}
      open={visible}
      onOk={form.submit}
      onCancel={onCancel}
      width={800}
      confirmLoading={submitLoading}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          type: '普货',
          status: 'active',
          category: '未分类',
          cost: 0,
          freightCost: 0,
          stock: 0,
          alertThreshold: 10
        }}
        onFinish={onFinish}
      >
        <Alert
          message="SKU 规则说明"
          description="SKU 必须由 6-30 位大写字母、数字、连字符或下划线组成。创建后不可修改。"
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="sku"
              label="SKU"
              rules={[
                { required: true, message: 'SKU是必填项' },
                { 
                  pattern: /^[A-Z0-9\-_]{6,30}$/, 
                  message: 'SKU只能包含大写字母、数字、连字符和下划线，长度6-30位' 
                }
              ]}
            >
              <Input 
                disabled={isEdit}
                placeholder="请输入SKU" 
                maxLength={30}
                showCount
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="chineseName"
              label="中文名"
              rules={[{ required: true, message: '中文名是必填项' }]}
            >
              <Input placeholder="请输入中文名" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="type"
              label="类型"
              rules={[{ required: true, message: '类型是必填项' }]}
            >
              <Select>
                <Select.Option value="普货">普货</Select.Option>
                <Select.Option value="纺织">纺织</Select.Option>
                <Select.Option value="混装">混装</Select.Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="category"
              label={
                <Space>
                  类别
                  <Tooltip title="用于商品分类管理，可自定义">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              }
            >
              <Input placeholder="请输入类别" />
            </Form.Item>
          </Col>
          <Col span={8}>
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
          </Col>
        </Row>

        <Divider orientation="left">价格信息</Divider>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="cost"
              label="成本价"
              rules={[
                { required: true, message: '成本价是必填项' },
                { type: 'number', min: 0, message: '成本价不能小于0' }
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                placeholder="请输入成本价"
                precision={2}
                prefix="¥"
                onChange={() => form.setFieldsValue({ totalCost: calculateTotalCost() })}
              />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="freightCost"
              label="头程运费"
              rules={[
                { required: true, message: '头程运费是必填项' },
                { type: 'number', min: 0, message: '头程运费不能小于0' }
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                placeholder="请输入头程运费"
                precision={2}
                prefix="¥"
                onChange={() => form.setFieldsValue({ totalCost: calculateTotalCost() })}
              />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              label="总成本"
            >
              <InputNumber
                style={{ width: '100%' }}
                value={calculateTotalCost()}
                disabled
                prefix="¥"
              />
            </Form.Item>
          </Col>
        </Row>

        <Divider orientation="left">库存信息</Divider>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="stock"
              label="当前库存"
              rules={[{ required: true, message: '请输入库存' }]}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="alertThreshold"
              label={
                <Space>
                  库存预警阈值
                  <Tooltip title="当库存低于此值时会发出预警">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              }
              rules={[{ required: true, message: '请设置库存预警阈值' }]}
            >
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="description"
          label="商品描述"
        >
          <Input.TextArea 
            rows={4} 
            placeholder="请输入商品描述信息"
            showCount
            maxLength={500}
          />
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
          extra="支持 jpg、png 格式，单张图片不超过 2MB，最多上传 5 张"
        >
          <Upload {...uploadProps}>
            {fileList.length >= 5 ? null : (
              <div>
                {uploading ? <LoadingOutlined /> : <PlusOutlined />}
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