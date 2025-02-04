# ANY-GO WebApp 项目规格说明书

## 1. 项目概述
跨境电商ERP系统，主要用于管理产品和装箱单等信息。
每次修改代码时，都要更新这个文档，并查看整个项目的代码，避免重复造轮子。
通过上传装箱单和采购单，自动创建产品，并计算成本价和头程运费。
同时计算出每个产品在在途的库存情况
帮助跨境电商运营工作
## 2. 核心功能

### 2.1 产品管理
- SKU管理
  - SKU唯一性验证
  - SKU格式验证
  - SKU批量导入
- 产品信息维护
  - 基本信息：SKU、中文名、类型
  - 类型信息：普货/纺织/混装
  - 价格信息：成本价，头程运费
  
- 批量导入导出
  - Excel模板下载
  - 批量导入验证
  - 导出当前筛选结果
- 自动创建缺失SKU
  - 导入装箱单时自动创建
  - 使用默认值填充

### 2.2 装箱单管理
- Excel导入功能
  - 文件命名规则："{店铺名}海运ERP.xlsx"
  - 自动提取店铺信息
  - 自动创建缺失SKU
  - 类型验证（普货/纺织/混装）
- 装箱单列表显示
  - 基本信息：店铺、日期、类型
  - 汇总信息：总箱数、总重量、总体积
  - 状态标识：已审核/未审核
- 装箱单详情页
  - 表头信息展示
  - 商品清单
  - 箱号分组显示
  - 合计信息
- 删除功能
  - 删除确认
  - 批量删除

## 3. 数据规则

### 3.1 装箱单Excel格式
- 每个sheet代表一个装箱单
- 跳过"常用箱规"sheet
- 表头信息位置：
  - D1单元格: 类型（普货/纺织/混装）
  - B1单元格: 总箱数
  - B2单元格: 总重量
  - B3单元格: 总体积
  - B4单元格: 总边加一体积
  - B6单元格: 总件数
  - D2单元格: 总价格

- 箱规信息（每个箱子占用3列）：
  - 1号箱：
    - F1,G1,H1: 箱规（长宽高）
    - F2: 箱重
    - F3: 体积
    - F4: 单边+1体积
    - F6: 该箱总件数
    - F7: 箱号（值为1）
  - 2号箱：
    - I1,J1,K1: 箱规（长宽高）
    - I2: 箱重
    - I3: 体积
    - I4: 单边+1体积
    - I6: 该箱总件数
    - I7: 箱号（值为2）
  - 后续箱号以此类推，每个箱子向右平移3列

- 商品数据（从第8行开始）：
  - A列：图片
  - B列：SKU
  - C列：中文名
  - F列及后续：各箱数量
    - F8及以下：该SKU在1号箱的数量
    - I8及以下：该SKU在2号箱的数量
    - 以此类推

### 3.2 自动创建SKU规则
- 触发条件：导入装箱单时遇到不存在的SKU
- 默认值设置：
  - 中文名: "待补充(SKU编号)"
  - 类型: 继承自装箱单类型
  - 价格相关: 0
  - 图片: 空
- 标记为待完善

### 3.3 产品类型规则
- 类型定义：
  - 普货：普通商品
  - 纺织：服装、布料等纺织品
  - 混装：可包含普货和纺织的混合装箱
- 装箱单验证：
  - 普货装箱单：仅允许普货产品
  - 纺织装箱单：仅允许纺织产品
  - 混装装箱单：允许所有类型产品

## 4. 用户界面规范
- 响应式设计
  - 支持桌面端
  - 适配大屏显示
- 列表页面
  - 批量操作栏
  - 筛选搜索区
  - 分页显示
- 表单设计
  - 分组展示
  - 必填项标识
  - 实时验证
- 操作反馈
  - 加载状态
  - 成功/错误提示
  - 确认对话框

## 5. 系统功能
### 5.1 用户权限管理
- 用户模型设计
  - 基本信息：用户名、密码（加密存储）
  - 角色分配
  - 权限控制
- 权限管理界面
  - 用户列表
  - 角色分配
  - 权限设置

### 5.2 操作日志
- 日志记录中间件
  - 用户操作记录
  - 系统事件记录
  - IP地址记录
- 日志查看界面
  - 按时间筛选
  - 按操作类型筛选
  - 按用户筛选
- 日志分析统计
  - 操作频率统计
  - 异常操作分析
- 自动清理机制
  - 定期清理过期日志
  - 可配置保留天数

### 5.3 数据备份
- 手动备份功能
  - 全量备份
  - 选择性备份
- 自动备份计划
  - 每日全量备份（凌晨3点）
  - 每6小时增量备份
  - 备份文件压缩
- 备份管理界面
  - 备份列表
  - 恢复功能
  - 下载备份
- 备份策略
  - 本地存储
  - 远程存储（待实现）

### 5.4 定时任务
- 任务调度系统
  - node-schedule 实现
  - 自动备份任务
  - 日志清理任务
- 任务管理
  - 任务状态监控
  - 执行记录查看
  - 手动触发功能

## 6. 技术实现
### 6.1 前端架构
- HTTP 请求处理
  - Axios 实例配置
  - 请求/响应拦截器
  - 统一错误处理
  - Token 认证
- 状态管理
  - React Context
  - 用户状态
  - 全局配置
- UI组件
  - Ant Design
  - 自定义组件
  - 响应式设计

### 6.2 后端架构
- Express 中间件
  - 身份认证
  - 日志记录
  - 错误处理
- 数据库设计
  - MongoDB Schema
  - 索引优化
  - 关联查询
- 进程管理
  - PM2 部署
  - 日志管理
  - 自动重启

### 6.3 部署方案
- 本地部署
  - PM2 进程管理
  - 日志文件管理
  - 环境变量配置
- 开发环境
  - 热重载
  - 调试配置
  - 测试数据

## 7. 安全性
- 身份认证
  - JWT Token
  - Token 刷新机制
  - 密码加密存储
- 权限控制
  - 基于角色的访问控制
  - API 权限验证
  - 资源访问控制
- 数据安全
  - 备份机制
  - 数据验证
  - 敏感信息加密

## 8. 性能优化
- 前端优化
  - 按需加载
  - 缓存策略
  - 压缩资源
- 后端优化
  - 数据库索引
  - 查询优化
  - 并发处理
- 监控告警
  - 性能监控
  - 错误告警
  - 资源使用监控
## 代码规范

### TypeScript 规范

1. 类型定义
   - 使用接口（interface）定义对象类型
   - 使用类型别名（type）定义联合类型或交叉类型
   - 所有类型名使用大驼峰命名法
   - 接口名不要使用 I 前缀
   ```typescript
   // 正确
   interface User {
     id: string;
     name: string;
   }
   
   // 错误
   interface IUser {
     id: string;
     name: string;
   }
   ```

2. 变量声明
   - 优先使用 const，其次是 let
   - 禁止使用 var
   - 变量名使用小驼峰命名法
   ```typescript
   // 正确
   const userName = 'John';
   let userAge = 25;
   
   // 错误
   var user_name = 'John';
   ```

3. 函数定义
   - 函数名使用小驼峰命名法
   - 必须明确参数类型和返回值类型
   - 异步函数必须返回 Promise
   ```typescript
   // 正确
   async function getUserById(id: string): Promise<User> {
     return await userService.findById(id);
   }
   
   // 错误
   async function get_user_by_id(id) {
     return userService.findById(id);
   }
   ```

### React 组件规范

1. 组件定义
   - 使用函数组件和 Hooks
   - 组件名使用大驼峰命名法
   - Props 类型必须明确定义
   ```typescript
   interface UserListProps {
     users: User[];
     onUserSelect: (user: User) => void;
   }
   
   const UserList: React.FC<UserListProps> = ({ users, onUserSelect }) => {
     // 组件实现
   };
   ```

2. Hooks 使用
   - 自定义 Hook 必须以 use 开头
   - 依赖数组必须完整
   - 避免过深的 Hook 嵌套
   ```typescript
   // 正确
   const useUserData = (userId: string) => {
     const [user, setUser] = useState<User | null>(null);
     
     useEffect(() => {
       fetchUser(userId).then(setUser);
     }, [userId]);
     
     return user;
   };
   ```

3. 状态管理
   - 局部状态使用 useState
   - 复杂状态使用 useReducer
   - 共享状态使用 Context

### 目录结构规范

```
client/
├── src/
│   ├── components/      # 组件目录
│   │   ├── common/      # 通用组件
│   │   ├── layout/      # 布局组件
│   │   └── pages/       # 页面组件
│   ├── hooks/           # 自定义 Hooks
│   ├── services/        # API 服务
│   ├── types/           # 类型定义
│   ├── utils/           # 工具函数
│   └── App.tsx          # 根组件
│
server/
├── src/
│   ├── controllers/     # 控制器
│   ├── models/          # 数据模型
│   ├── routes/          # 路由定义
│   ├── services/        # 业务逻辑
│   └── utils/           # 工具函数
```

## 数据规范

### 商品数据

1. SKU 规则
   - 格式：`^[A-Z0-9\-_]{6,30}$`
   - 示例：`PRODUCT-001`, `TEXTILE_SHIRT_L`
   - 唯一性：系统级别唯一
   - 不可修改性：创建后不可修改

2. 商品类型
   ```typescript
   type ProductType = 'normal' | 'textile' | 'mixed';
   ```
   - normal: 普货
   - textile: 纺织
   - mixed: 混装

3. 商品状态
   ```typescript
   type ProductStatus = 'active' | 'inactive';
   ```
   - active: 上架
   - inactive: 下架

### 装箱单数据

1. 箱号规则
   - 格式：字母数字组合
   - 示例：`BOX001`, `A001`
   - 范围：同一装箱单内唯一

2. 装箱单状态
   ```typescript
   type PackingListStatus = 'pending' | 'approved';
   ```
   - pending: 待审核
   - approved: 已审核

3. 重量和体积
   - 重量单位：kg
   - 体积单位：m³
   - 精度：重量保留2位小数，体积保留3位小数

## API 规范

### 请求规范

1. URL 规则
   - 使用小写字母
   - 使用连字符（-）连接单词
   - 使用复数形式表示资源集合
   ```
   /api/products
   /api/packing-lists
   ```

2. HTTP 方法
   - GET：查询
   - POST：创建
   - PUT：完整更新
   - PATCH：部分更新
   - DELETE：删除

3. 查询参数
   ```typescript
   interface QueryParams {
     page?: number;
     pageSize?: number;
     keyword?: string;
     [key: string]: any;
   }
   ```

### 响应规范

1. 成功响应
   ```typescript
   interface ApiResponse<T> {
     code: 0;
     data: T;
     message: string;
   }
   ```

2. 错误响应
   ```typescript
   interface ApiError {
     code: number;
     message: string;
     details?: any;
   }
   ```

3. 状态码使用
   - 200：成功
   - 201：创建成功
   - 400：请求错误
   - 401：未授权
   - 403：禁止访问
   - 404：资源不存在
   - 500：服务器错误

## 文档规范

### 代码注释

1. 文件头注释
   ```typescript
   /**
    * @file 文件描述
    * @author 作者
    * @date 创建日期
    */
   ```

2. 函数注释
   ```typescript
   /**
    * 函数描述
    * @param {string} param1 参数1描述
    * @param {number} param2 参数2描述
    * @returns {Promise<Result>} 返回值描述
    * @throws {Error} 可能抛出的错误
    */
   ```

3. 接口注释
   ```typescript
   /**
    * 用户信息接口
    * @interface User
    */
   interface User {
     /** 用户ID */
     id: string;
     /** 用户名 */
     name: string;
   }
   ```

### Git 规范

1. 分支命名
   - 主分支：master/main
   - 开发分支：develop
   - 功能分支：feature/xxx
   - 修复分支：hotfix/xxx
   - 发布分支：release/xxx

2. 提交信息
   ```
   <type>(<scope>): <subject>

   <body>

   <footer>
   ```
   - type: feat, fix, docs, style, refactor, test, chore
   - scope: 影响范围
   - subject: 简短描述
   - body: 详细描述
   - footer: 关闭 issue 等

3. 版本号规范
   - 遵循语义化版本 2.0.0
   - 格式：主版本号.次版本号.修订号
   - 示例：1.0.0, 1.0.1, 1.1.0

## 测试规范

1. 单元测试
   - 使用 Jest 框架
   - 测试文件命名：*.test.ts
   - 覆盖率要求：>= 80%

2. 组件测试
   - 使用 React Testing Library
   - 测试用户交互
   - 测试渲染结果

3. 端到端测试
   - 使用 Cypress
   - 测试关键业务流程
   - 测试用户场景

## 安全规范

1. 身份认证
   - 使用 JWT
   - Token 过期时间：24小时
   - 刷新 Token 机制

2. 数据验证
   - 使用 Joi 进行请求验证
   - 使用 TypeScript 类型检查
   - SQL 注入防护

3. 敏感信息
   - 密码必须加密存储
   - API Key 必须加密
   - 日志脱敏处理

## 性能规范

1. 前端优化
   - 代码分割
   - 懒加载
  - 缓存策略
   - 图片优化

2. 后端优化
  - 数据库索引
   - 缓存使用
   - 并发控制
   - 连接池管理

3. 监控指标
   - 响应时间
   - 错误率
   - 资源使用率
   - 用户体验指标



