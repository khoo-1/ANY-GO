import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, DatePicker, Select, Button, message, Space, Table } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { Line } from '@ant-design/plots';
import profitService, { ProfitSummary } from '../../services/profitService';
import { formatCurrency, formatPercent } from '../../utils/format';

const { RangePicker } = DatePicker;

const ProfitAnalysis: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<ProfitSummary | null>(null);
  const [dateRange, setDateRange] = useState<[string, string] | null>(null);

  // 加载利润汇总数据
  const loadSummary = async () => {
    try {
      setLoading(true);
      const params = dateRange ? {
        startDate: dateRange[0],
        endDate: dateRange[1]
      } : {};
      const data = await profitService.getProfitSummary(params);
      setSummary(data);
    } catch (error) {
      message.error('加载利润汇总数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, [dateRange]);

  // 计算利润分析
  const handleCalculate = async () => {
    try {
      setLoading(true);
      const today = new Date().toISOString().split('T')[0];
      await profitService.calculateAnalysis(today, 'daily');
      message.success('利润分析计算完成');
      loadSummary();
    } catch (error) {
      message.error('利润分析计算失败');
    } finally {
      setLoading(false);
    }
  };

  // 利润趋势图配置
  const trendConfig = {
    data: summary?.profitTrend || [],
    xField: 'date',
    yField: 'value',
    seriesField: 'type',
    yAxis: {
      label: {
        formatter: (v: string) => formatCurrency(Number(v))
      }
    },
    legend: {
      position: 'top'
    }
  };

  // 处理趋势图数据
  const trendData = summary?.profitTrend.reduce((acc: any[], item) => {
    return acc.concat([
      { date: item.date, type: '销售额', value: item.totalSales },
      { date: item.date, type: '毛利润', value: item.grossProfit },
      { date: item.date, type: '净利润', value: item.netProfit }
    ]);
  }, []) || [];

  return (
    <div className="profit-analysis">
      <div className="page-header" style={{ marginBottom: 24 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <h2>利润分析</h2>
          </Col>
          <Col>
            <Space>
              <RangePicker
                onChange={(dates) => {
                  if (dates) {
                    setDateRange([
                      dates[0]!.format('YYYY-MM-DD'),
                      dates[1]!.format('YYYY-MM-DD')
                    ]);
                  } else {
                    setDateRange(null);
                  }
                }}
              />
              <Button type="primary" onClick={handleCalculate} loading={loading}>
                计算利润
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      <Row gutter={[24, 24]}>
        {/* 利润概览 */}
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="总销售额"
              value={summary?.totalSales}
              prefix="¥"
              precision={2}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="毛利润"
              value={summary?.overallGrossProfit}
              prefix="¥"
              precision={2}
              valueStyle={{ color: '#3f8600' }}
            />
            <div style={{ fontSize: 14, color: '#666' }}>
              毛利率：{formatPercent(summary?.overallGrossProfitRate)}
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="净利润"
              value={summary?.overallNetProfit}
              prefix="¥"
              precision={2}
              valueStyle={{ color: summary?.overallNetProfit >= 0 ? '#3f8600' : '#cf1322' }}
            />
            <div style={{ fontSize: 14, color: '#666' }}>
              净利率：{formatPercent(summary?.overallNetProfitRate)}
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="总成本"
              value={summary?.totalCost}
              prefix="¥"
              precision={2}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>

        {/* 利润趋势图 */}
        <Col span={24}>
          <Card title="利润趋势" loading={loading}>
            <Line {...trendConfig} data={trendData} height={300} />
          </Card>
        </Col>

        {/* 商品利润排名 */}
        <Col span={12}>
          <Card title="利润最高商品" loading={loading}>
            <ul className="profit-rank-list">
              {summary?.topProfitProducts.map((item, index) => (
                <li key={item.id}>
                  <span className="rank-number">#{index + 1}</span>
                  <span className="product-info">
                    <div className="product-name">{item.name}</div>
                    <div className="product-sku">{item.sku}</div>
                  </span>
                  <span className="profit-info">
                    <div className="profit-amount">
                      {formatCurrency(item.netProfit)}
                    </div>
                    <div className="profit-rate">
                      {formatPercent(item.profitRate)}
                    </div>
                  </span>
                </li>
              ))}
            </ul>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="利润最低商品" loading={loading}>
            <ul className="profit-rank-list">
              {summary?.bottomProfitProducts.map((item, index) => (
                <li key={item.id}>
                  <span className="rank-number">#{index + 1}</span>
                  <span className="product-info">
                    <div className="product-name">{item.name}</div>
                    <div className="product-sku">{item.sku}</div>
                  </span>
                  <span className="profit-info">
                    <div className="profit-amount">
                      {formatCurrency(item.netProfit)}
                    </div>
                    <div className="profit-rate">
                      {formatPercent(item.profitRate)}
                    </div>
                  </span>
                </li>
              ))}
            </ul>
          </Card>
        </Col>

        {/* 品类分析 */}
        <Col span={24}>
          <Card title="品类分析" loading={loading}>
            <Table
              dataSource={summary?.categoryAnalysis}
              columns={[
                {
                  title: '品类',
                  dataIndex: 'category',
                  key: 'category',
                },
                {
                  title: '销售额',
                  dataIndex: 'salesAmount',
                  key: 'salesAmount',
                  render: (value) => formatCurrency(value),
                  sorter: (a, b) => a.salesAmount - b.salesAmount,
                },
                {
                  title: '净利润',
                  dataIndex: 'netProfit',
                  key: 'netProfit',
                  render: (value) => formatCurrency(value),
                  sorter: (a, b) => a.netProfit - b.netProfit,
                },
                {
                  title: '利润率',
                  dataIndex: 'profitRate',
                  key: 'profitRate',
                  render: (value) => formatPercent(value),
                  sorter: (a, b) => a.profitRate - b.profitRate,
                },
                {
                  title: '平均订单金额',
                  dataIndex: 'avgOrderValue',
                  key: 'avgOrderValue',
                  render: (value) => formatCurrency(value),
                  sorter: (a, b) => a.avgOrderValue - b.avgOrderValue,
                },
                {
                  title: '平均订单利润',
                  dataIndex: 'avgProfitPerOrder',
                  key: 'avgProfitPerOrder',
                  render: (value) => formatCurrency(value),
                  sorter: (a, b) => a.avgProfitPerOrder - b.avgProfitPerOrder,
                },
              ]}
              pagination={false}
            />
          </Card>
        </Col>
      </Row>

      <style>
        {`
          .profit-rank-list {
            list-style: none;
            padding: 0;
            margin: 0;
          }
          .profit-rank-list li {
            display: flex;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
          }
          .profit-rank-list li:last-child {
            border-bottom: none;
          }
          .rank-number {
            width: 48px;
            text-align: center;
            font-size: 16px;
            color: #999;
          }
          .product-info {
            flex: 1;
          }
          .product-name {
            font-size: 14px;
            color: #333;
          }
          .product-sku {
            font-size: 12px;
            color: #999;
          }
          .profit-info {
            text-align: right;
            margin-left: 24px;
          }
          .profit-amount {
            font-size: 16px;
            color: #333;
          }
          .profit-rate {
            font-size: 12px;
            color: #999;
          }
        `}
      </style>
    </div>
  );
};

export default ProfitAnalysis; 