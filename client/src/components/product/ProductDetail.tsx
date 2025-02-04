import React from 'react';
import { Modal, Descriptions, Image, Tag, Space, Typography, Divider } from 'antd';
import { Product } from '../../types/api';

const { Title } = Typography;

interface ProductDetailProps {
  visible: boolean;
  product: Product | null;
  onClose: () => void;
}

const ProductDetail: React.FC<ProductDetailProps> = ({
  visible,
  product,
  onClose
}) => {
  if (!product) return null;

  const typeColors = {
    '普货': 'blue',
    '纺织': 'green',
    '混装': 'orange'
  };

  return (
    <Modal
      title="商品详情"
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
    >
      <div style={{ padding: '0 24px' }}>
        <Title level={4}>{product.chineseName}</Title>
        <Tag color={typeColors[product.type as keyof typeof typeColors]}>
          {product.type}
        </Tag>

        <Divider orientation="left">基本信息</Divider>
        <Descriptions column={2}>
          <Descriptions.Item label="SKU">{product.sku}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={product.status === 'active' ? 'success' : 'default'}>
              {product.status === 'active' ? '上架' : '下架'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="类别">{product.category || '未分类'}</Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {new Date(product.createdAt).toLocaleString()}
          </Descriptions.Item>
        </Descriptions>

        <Divider orientation="left">价格信息</Divider>
        <Descriptions column={2}>
          <Descriptions.Item label="成本价">
            ¥{(product.cost || 0).toFixed(2)}
          </Descriptions.Item>
          <Descriptions.Item label="头程运费">
            ¥{(product.freightCost || 0).toFixed(2)}
          </Descriptions.Item>
          <Descriptions.Item label="总成本">
            ¥{((product.cost || 0) + (product.freightCost || 0)).toFixed(2)}
          </Descriptions.Item>
        </Descriptions>

        <Divider orientation="left">库存信息</Divider>
        <Descriptions column={2}>
          <Descriptions.Item label="当前库存">
            {product.stock || 0}
          </Descriptions.Item>
          <Descriptions.Item label="库存预警阈值">
            {product.alertThreshold || 10}
          </Descriptions.Item>
          <Descriptions.Item label="库存状态">
            <Tag color={(product.stock || 0) > (product.alertThreshold || 10) ? 'success' : 'warning'}>
              {(product.stock || 0) > (product.alertThreshold || 10) ? '库存充足' : '库存不足'}
            </Tag>
          </Descriptions.Item>
        </Descriptions>

        {product.description && (
          <>
            <Divider orientation="left">商品描述</Divider>
            <p style={{ whiteSpace: 'pre-wrap' }}>{product.description}</p>
          </>
        )}

        {product.images && product.images.length > 0 && (
          <>
            <Divider orientation="left">商品图片</Divider>
            <Space size={16} wrap>
              {product.images.map((url, index) => (
                <Image
                  key={index}
                  src={url}
                  width={120}
                  height={120}
                  style={{ objectFit: 'cover' }}
                />
              ))}
            </Space>
          </>
        )}
      </div>
    </Modal>
  );
};

export default ProductDetail; 