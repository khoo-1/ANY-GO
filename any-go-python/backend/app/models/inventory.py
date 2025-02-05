from sqlalchemy import Column, String, Float, Integer, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class InventoryAnalysisType(str, enum.Enum):
    """库存分析类型"""
    DAILY = "daily"  # 日度分析
    WEEKLY = "weekly"  # 周度分析
    MONTHLY = "monthly"  # 月度分析

class InventoryAnalysis(BaseModel):
    """库存分析"""
    __tablename__ = "inventory_analysis"

    date = Column(Date, nullable=False, index=True)  # 分析日期
    type = Column(Enum(InventoryAnalysisType), nullable=False)  # 分析类型
    
    # 库存总览
    total_products = Column(Integer, default=0)  # 商品总数
    total_quantity = Column(Integer, default=0)  # 库存总量
    total_value = Column(Float, default=0)  # 库存总值
    
    # 周转率指标
    turnover_rate = Column(Float, default=0)  # 周转率
    turnover_days = Column(Float, default=0)  # 周转天数
    average_inventory = Column(Float, default=0)  # 平均库存
    inventory_cost = Column(Float, default=0)  # 库存成本
    
    # 库存结构
    active_products = Column(Integer, default=0)  # 动销商品数
    inactive_products = Column(Integer, default=0)  # 呆滞商品数
    stockout_products = Column(Integer, default=0)  # 缺货商品数
    overstock_products = Column(Integer, default=0)  # 积压商品数
    
    # 库存健康度
    healthy_stock_ratio = Column(Float, default=0)  # 健康库存比例
    stockout_ratio = Column(Float, default=0)  # 缺货率
    overstock_ratio = Column(Float, default=0)  # 积压率

class ProductTurnover(BaseModel):
    """商品周转分析"""
    __tablename__ = "product_turnover"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    date = Column(Date, nullable=False)  # 分析日期
    type = Column(Enum(InventoryAnalysisType), nullable=False)  # 分析类型
    
    # 基础数据
    beginning_stock = Column(Integer, default=0)  # 期初库存
    ending_stock = Column(Integer, default=0)  # 期末库存
    average_stock = Column(Float, default=0)  # 平均库存
    sales_quantity = Column(Integer, default=0)  # 销售数量
    sales_amount = Column(Float, default=0)  # 销售金额
    
    # 周转指标
    turnover_rate = Column(Float, default=0)  # 周转率
    turnover_days = Column(Float, default=0)  # 周转天数
    stock_status = Column(String, nullable=True)  # 库存状态（正常/积压/缺货）
    
    # 关联
    product = relationship("Product", backref="turnover_analysis")

    class Config:
        unique_together = [("product_id", "date", "type")]

class CategoryTurnover(BaseModel):
    """品类周转分析"""
    __tablename__ = "category_turnover"

    category = Column(String, nullable=False)  # 商品类别
    date = Column(Date, nullable=False)  # 分析日期
    type = Column(Enum(InventoryAnalysisType), nullable=False)  # 分析类型
    
    # 基础数据
    total_products = Column(Integer, default=0)  # 商品总数
    total_stock = Column(Integer, default=0)  # 库存总量
    total_value = Column(Float, default=0)  # 库存总值
    sales_quantity = Column(Integer, default=0)  # 销售数量
    sales_amount = Column(Float, default=0)  # 销售金额
    
    # 周转指标
    turnover_rate = Column(Float, default=0)  # 周转率
    turnover_days = Column(Float, default=0)  # 周转天数
    
    # 库存结构
    active_products = Column(Integer, default=0)  # 动销商品数
    inactive_products = Column(Integer, default=0)  # 呆滞商品数
    stockout_products = Column(Integer, default=0)  # 缺货商品数
    overstock_products = Column(Integer, default=0)  # 积压商品数

    class Config:
        unique_together = [("category", "date", "type")] 