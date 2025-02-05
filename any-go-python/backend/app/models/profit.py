from sqlalchemy import Column, String, Float, Integer, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ProfitAnalysisType(str, enum.Enum):
    """利润分析类型"""
    DAILY = "daily"  # 日度分析
    WEEKLY = "weekly"  # 周度分析
    MONTHLY = "monthly"  # 月度分析

class ProfitAnalysis(BaseModel):
    """利润分析"""
    __tablename__ = "profit_analysis"

    date = Column(Date, nullable=False, index=True)  # 分析日期
    type = Column(Enum(ProfitAnalysisType), nullable=False)  # 分析类型
    
    # 销售数据
    total_orders = Column(Integer, default=0)  # 订单总数
    total_sales = Column(Float, default=0)  # 销售总额
    
    # 成本数据
    product_cost = Column(Float, default=0)  # 商品成本
    shipping_cost = Column(Float, default=0)  # 运输成本
    operation_cost = Column(Float, default=0)  # 运营成本
    other_cost = Column(Float, default=0)  # 其他成本
    total_cost = Column(Float, default=0)  # 总成本
    
    # 利润数据
    gross_profit = Column(Float, default=0)  # 毛利润
    net_profit = Column(Float, default=0)  # 净利润
    gross_profit_rate = Column(Float, default=0)  # 毛利率
    net_profit_rate = Column(Float, default=0)  # 净利率

    class Config:
        unique_together = [("date", "type")]

class ProductProfit(BaseModel):
    """商品利润分析"""
    __tablename__ = "product_profit"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    date = Column(Date, nullable=False)  # 分析日期
    type = Column(Enum(ProfitAnalysisType), nullable=False)  # 分析类型
    
    # 销售数据
    sales_quantity = Column(Integer, default=0)  # 销售数量
    sales_amount = Column(Float, default=0)  # 销售金额
    
    # 成本数据
    unit_cost = Column(Float, default=0)  # 单位成本
    total_cost = Column(Float, default=0)  # 总成本
    shipping_cost = Column(Float, default=0)  # 运输成本
    
    # 利润数据
    gross_profit = Column(Float, default=0)  # 毛利润
    net_profit = Column(Float, default=0)  # 净利润
    gross_profit_rate = Column(Float, default=0)  # 毛利率
    net_profit_rate = Column(Float, default=0)  # 净利率
    
    # 关联
    product = relationship("Product", backref="profit_analysis")

    class Config:
        unique_together = [("product_id", "date", "type")]

class CategoryProfit(BaseModel):
    """品类利润分析"""
    __tablename__ = "category_profit"

    category = Column(String, nullable=False)  # 商品类别
    date = Column(Date, nullable=False)  # 分析日期
    type = Column(Enum(ProfitAnalysisType), nullable=False)  # 分析类型
    
    # 基础数据
    total_products = Column(Integer, default=0)  # 商品总数
    total_orders = Column(Integer, default=0)  # 订单总数
    
    # 销售数据
    sales_quantity = Column(Integer, default=0)  # 销售数量
    sales_amount = Column(Float, default=0)  # 销售金额
    
    # 成本数据
    product_cost = Column(Float, default=0)  # 商品成本
    shipping_cost = Column(Float, default=0)  # 运输成本
    operation_cost = Column(Float, default=0)  # 运营成本
    
    # 利润数据
    gross_profit = Column(Float, default=0)  # 毛利润
    net_profit = Column(Float, default=0)  # 净利润
    gross_profit_rate = Column(Float, default=0)  # 毛利率
    net_profit_rate = Column(Float, default=0)  # 净利率
    
    # 平均值
    average_order_value = Column(Float, default=0)  # 平均订单金额
    average_profit_per_order = Column(Float, default=0)  # 平均订单利润

    class Config:
        unique_together = [("category", "date", "type")] 