from sqlalchemy import Column, String, Enum, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
from .product import ProductType
import enum

class PackingListStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"

class BoxSpecs(BaseModel):
    """箱子规格模型"""
    __tablename__ = "box_specs"

    length = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    edge_volume = Column(Float, nullable=False)
    total_pieces = Column(Integer, nullable=False)
    packing_list_id = Column(Integer, ForeignKey("packing_lists.id"))

class PackingListItem(BaseModel):
    """装箱单明细模型"""
    __tablename__ = "packing_list_items"

    packing_list_id = Column(Integer, ForeignKey("packing_lists.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    box_quantities = Column(JSON, nullable=False)  # [{box_no: str, quantity: int}]
    
    # 关联
    product = relationship("Product")

class PackingList(BaseModel):
    """装箱单模型"""
    __tablename__ = "packing_lists"

    store_name = Column(String, nullable=False)
    type = Column(Enum(ProductType), nullable=False)
    status = Column(Enum(PackingListStatus), default=PackingListStatus.PENDING)
    
    # 汇总信息
    total_boxes = Column(Integer, nullable=False)
    total_weight = Column(Float, nullable=False)
    total_volume = Column(Float, nullable=False)
    total_pieces = Column(Integer, nullable=False)
    total_value = Column(Float, nullable=False)
    
    # 备注
    remarks = Column(String, nullable=True)
    
    # 关联
    items = relationship("PackingListItem", cascade="all, delete-orphan")
    box_specs = relationship("BoxSpecs", cascade="all, delete-orphan")

    @classmethod
    def extract_store_name(cls, filename: str) -> str:
        """从文件名提取店铺信息"""
        if not filename:
            raise ValueError("文件名不能为空")
            
        # 移除文件扩展名
        name_without_ext = filename.replace(".xlsx", "").replace(".xls", "")
        
        # 检查文件名格式
        suffix = "海运ERP"
        if not name_without_ext.endswith(suffix):
            raise ValueError(f"文件名格式错误，必须以"{suffix}"结尾")
            
        # 提取店铺名称
        store_name = name_without_ext[:-len(suffix)]
        if not store_name:
            raise ValueError('无法从文件名中提取店铺名称，请确保文件名格式为："{店铺名}海运ERP.xlsx"')
            
        return store_name 