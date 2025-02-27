def init_products(db: Session):
    """初始化产品数据"""
    # 检查是否已有产品数据
    if db.query(Product).count() == 0:
        # 示例产品数据
        products = [
            {
                "name": "智能手表",
                "sku": "SW-001",
                "description": "多功能智能手表，支持心率监测、运动追踪等功能",
                "price": 299.99,
                "cost": 150.00,
                "weight": 0.05,
                "stock": 100,
                "category": "电子产品",
                "tags": json.dumps(["智能穿戴", "电子产品", "热销"]),
                "type": "电子产品",
                "status": "active"
            },
            {
                "name": "便携式蓝牙音箱",
                "sku": "BS-002",
                "description": "高品质便携式蓝牙音箱，防水设计，续航时间长",
                "price": 89.99,
                "cost": 40.00,
                "weight": 0.3,
                "stock": 150,
                "category": "电子产品",
                "tags": json.dumps(["音频设备", "电子产品", "户外"]),
                "type": "电子产品",
                "status": "active"
            },
            {
                "name": "多功能厨房刀具套装",
                "sku": "KS-003",
                "description": "高品质不锈钢厨房刀具套装，包含主厨刀、面包刀、水果刀等",
                "price": 129.99,
                "cost": 60.00,
                "weight": 1.2,
                "stock": 80,
                "category": "厨房用品",
                "tags": json.dumps(["厨房用品", "家居", "套装"]),
                "type": "家居用品",
                "status": "active"
            }
        ]
        
        # 添加产品数据
        for product_data in products:
            product = Product(**product_data)
            db.add(product)
        
        db.commit()
        print("产品数据初始化成功") 