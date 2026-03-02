# 流浪动物云领养系统

## 项目简介

流浪动物云领养系统是一个基于Django和Vue.js的全栈应用，旨在为流浪动物提供一个在线领养平台，同时支持动物基地的管理和运营。系统涵盖了流浪动物信息管理、领养流程管理、用户管理、互动交流平台管理、志愿者管理和动物基地管理等核心模块。

## 技术栈

### 后端
- Django 6.0.2
- Django REST Framework
- SQLite (开发环境) / MySQL (生产环境)
- JWT 认证

### 前端
- Vue.js 3
- Vite
- Axios
- Vue Router

## 核心功能

### 1. 动物管理
- 流浪动物信息录入和管理
- 动物状态跟踪（可领养、已领养、医疗中等）
- 动物与基地的关联管理

### 2. 领养管理
- 在线领养申请提交
- 领养申请审核流程
- 领养记录管理

### 3. 用户管理
- 用户注册和登录
- JWT认证
- 用户个人中心

### 4. 社区互动
- 志愿者活动发布
- 互动申请管理（探访、寄养等）

### 5. 基地管理
- 动物基地创建和管理
- 基地活动日历
- 捐赠统计和管理
- 基地工作人员管理

### 6. 捐赠管理
- 金钱、物品、服务捐赠
- 捐赠记录跟踪
- 捐赠统计报表

## 项目结构

```
AnimalAdoptSystem/
├── adoptions/         # 领养相关功能
├── animals/           # 动物管理功能
├── backend/           # Django项目配置
├── community/         # 社区互动功能
├── frontend/          # Vue.js前端项目
├── shelters/          # 基地管理功能
├── users/             # 用户管理功能
├── db.sqlite3         # SQLite数据库文件
├── manage.py          # Django管理脚本
└── README.md          # 项目说明文件
```

## 环境要求

- Python 3.10+
- Node.js 16+
- npm 8+

## 安装和运行

### 1. 后端安装和运行

#### 步骤1: 克隆项目
```bash
git clone <项目地址>
cd AnimalAdoptSystem
```

#### 步骤2: 创建虚拟环境并激活
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 步骤3: 安装依赖
```bash
pip install -r requirements.txt
```

#### 步骤4: 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 步骤5: 创建超级用户（可选）
```bash
python manage.py createsuperuser
```

#### 步骤6: 启动后端服务器
```bash
python manage.py runserver
```

后端服务器默认运行在 http://127.0.0.1:8000/

### 2. 前端安装和运行

#### 步骤1: 进入前端目录
```bash
cd frontend
```

#### 步骤2: 安装依赖
```bash
npm install
```

#### 步骤3: 启动前端开发服务器
```bash
npm run dev
```

前端开发服务器默认运行在 http://localhost:3000/

## API文档

系统提供了完整的RESTful API，主要接口包括：

### 用户相关
- POST /api/token/ - 获取JWT令牌
- POST /api/token/refresh/ - 刷新JWT令牌
- POST /api/users/register/ - 用户注册
- GET /api/users/profile/ - 获取用户个人信息

### 动物相关
- GET /api/animals/ - 获取动物列表
- GET /api/animals/{id}/ - 获取动物详情
- POST /api/animals/ - 创建动物信息（管理员）
- PUT /api/animals/{id}/ - 更新动物信息（管理员）

### 领养相关
- GET /api/adoptions/ - 获取领养申请列表
- POST /api/adoptions/ - 提交领养申请
- PUT /api/adoptions/{id}/approve/ - 批准领养申请（管理员）
- PUT /api/adoptions/{id}/reject/ - 拒绝领养申请（管理员）

### 基地相关
- GET /api/shelters/ - 获取基地列表
- POST /api/shelters/ - 创建基地
- GET /api/shelters/{id}/ - 获取基地详情
- GET /api/activities/ - 获取活动列表
- POST /api/activities/ - 创建基地活动
- GET /api/donations/ - 获取捐赠记录
- POST /api/donations/ - 提交捐赠

## 测试功能

### 1. 后端API测试

使用Postman或curl测试API接口：

#### 示例1: 注册用户
```bash
curl -X POST http://127.0.0.1:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123", "email": "test@example.com"}'
```

#### 示例2: 获取动物列表
```bash
curl http://127.0.0.1:8000/api/animals/
```

### 2. 前端功能测试

1. 打开浏览器，访问 http://localhost:3000
2. 注册新用户
3. 浏览动物列表
4. 提交领养申请
5. 创建动物基地（测试基地管理员功能）
6. 发布基地活动
7. 测试捐赠功能

## 部署说明

### 生产环境部署

#### 后端部署
1. 使用Gunicorn或uWSGI作为WSGI服务器
2. 配置Nginx作为反向代理
3. 使用MySQL或PostgreSQL作为数据库
4. 配置环境变量，设置SECRET_KEY等敏感信息

#### 前端部署
1. 构建生产版本
```bash
npm run build
```
2. 将dist目录部署到Nginx或其他静态文件服务器
3. 配置Nginx代理后端API请求

### 环境变量配置

在生产环境中，建议通过环境变量配置以下信息：
- SECRET_KEY
- DATABASE_URL
- DEBUG=False
- ALLOWED_HOSTS

## 常见问题

### 1. 无法登录系统
- 检查用户名和密码是否正确
- 检查后端服务器是否运行
- 检查网络连接

### 2. 无法创建基地
- 确保已登录系统
- 检查表单填写是否完整
- 检查后端API是否正常响应

### 3. 前端页面加载缓慢
- 检查网络连接
- 检查后端服务器性能
- 考虑在生产环境中启用缓存

### 4. 数据库连接失败
- 检查数据库服务是否运行
- 检查数据库配置是否正确
- 检查数据库用户权限

## 贡献指南

1. Fork本项目
2. 创建功能分支
3. 提交代码
4. 发起Pull Request

