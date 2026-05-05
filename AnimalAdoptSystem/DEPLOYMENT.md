# 🚀 Sealos 云平台部署指南

## 📋 前置准备

1. 注册 Sealos 账号：https://hzh.sealos.run/
2. 安装 Git
3. 确保项目代码已推送到 GitHub/Gitee

---

## 🎯 部署步骤

### **第一步：上传代码到代码仓库**

```bash
# 如果还没有 Git 仓库，先初始化
cd D:\Code\python\AnimalAdoptSystem
git init
git add .
git commit -m "Initial commit"

# 推送到 GitHub 或 Gitee
git remote add origin https://github.com/your-username/AnimalAdoptSystem.git
git push -u origin main
```

### **第二步：在 Sealos 上创建应用**

#### **1. 登录 Sealos 控制台**
访问：https://hzh.sealos.run/

#### **2. 创建 MySQL 数据库**
- 点击「应用管理」→「新建应用」
- 选择「数据库」→「MySQL 8.0」
- 配置：
  - 应用名称：`animal-db`
  - CPU：1 Core
  - 内存：1 GiB
  - 存储：10 GiB
- 记录数据库连接信息（主机、端口、密码）

#### **3. 创建 Redis 缓存**
- 选择「数据库」→「Redis 7.0」
- 配置：
  - 应用名称：`animal-redis`
  - CPU：0.5 Core
  - 内存：512 MiB
- 记录 Redis 连接地址

#### **4. 部署 Django 后端**
- 选择「应用开发」→「Web 应用」
- 配置：
  - 应用名称：`animal-backend`
  - 代码来源：选择你的 GitHub/Gitee 仓库
  - 分支：`main`
  - 构建目录：`/AnimalAdoptSystem`（如果有子目录）
  - Dockerfile 路径：`Dockerfile`
  
- **环境变量配置**（重要！）：
  ```
  DEBUG=False
  DB_HOST=<MySQL服务地址>
  DB_PORT=3306
  DB_NAME=animaladoptsystem
  DB_USER=root
  DB_PASSWORD=<MySQL密码>
  REDIS_HOST=<Redis服务地址>
  REDIS_PORT=6379
  SECRET_KEY=<生成一个随机密钥>
  ALLOWED_HOSTS=*
  ```

- 资源配置：
  - CPU：2 Core
  - 内存：2 GiB
  - 实例数：1

- 端口配置：
  - 容器端口：8000
  - 协议：HTTP

#### **5. 部署 Vue 前端**
- 选择「应用开发」→「Web 应用」
- 配置：
  - 应用名称：`animal-frontend`
  - 代码来源：同一仓库
  - 构建目录：`/frontend`
  - Dockerfile 路径：`frontend/Dockerfile`

- 环境变量配置：
  ```
  VITE_API_BASE_URL=http://<后端服务地址>:8000
  ```

- 资源配置：
  - CPU：1 Core
  - 内存：512 MiB

- 端口配置：
  - 容器端口：80
  - 协议：HTTP

#### **6. 配置域名和 HTTPS**
- 在 Sealos 控制台为前端应用绑定域名
- 启用 HTTPS（Sealos 免费提供 SSL 证书）

---

## 🔧 本地测试 Docker 部署

在上传到 Sealos 之前，建议先在本地测试 Docker 构建：

```bash
# 进入项目根目录
cd D:\Code\python\AnimalAdoptSystem\AnimalAdoptSystem

# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

访问：
- 前端：http://localhost
- 后端 API：http://localhost:8000/api/
- Admin 后台：http://localhost:8000/admin/

---

## 📝 常见问题

### **1. 数据库连接失败**
- 检查 Sealos 中 MySQL 服务的内网地址
- 确保环境变量 `DB_HOST` 配置正确
- 验证密码是否正确

### **2. Redis 连接超时**
- 检查 Redis 服务是否正常运行
- 确认 `REDIS_HOST` 使用内网地址

### **3. 静态文件 404**
- 确保 `collectstatic` 命令执行成功
- 检查 Nginx 配置中的静态文件路径

### **4. CORS 跨域问题**
- 后端 `ALLOWED_HOSTS` 需包含前端域名
- 确认 `CORS_ORIGIN_ALLOW_ALL = True`

### **5. 媒体文件无法访问**
- 确保后端容器挂载了持久化存储卷
- 检查 `MEDIA_ROOT` 路径权限

---

## 🎉 部署完成检查清单

- [ ] MySQL 数据库正常运行
- [ ] Redis 缓存服务正常
- [ ] 后端 API 可访问（返回 JSON）
- [ ] 前端页面正常加载
- [ ] 用户注册/登录功能正常
- [ ] 图片上传功能正常
- [ ] WebSocket 实时通知正常（如需要）
- [ ] HTTPS 证书配置成功

---

## 📊 监控和维护

### **查看日志**
```bash
# Sealos 控制台 → 应用详情 → 日志
# 或使用命令行
sealos logs animal-backend
```

### **重启服务**
```bash
# Sealos 控制台 → 应用详情 → 重启
```

### **数据库备份**
- Sealos 提供自动备份功能
- 也可手动导出：
  ```bash
  mysqldump -h <host> -u root -p animaladoptsystem > backup.sql
  ```

---

## 💰 成本估算（Sealos 按量计费）

| 服务 | 配置 | 月费用（约） |
|------|------|-------------|
| MySQL | 1C1G + 10GB | ¥30-50 |
| Redis | 0.5C512M | ¥15-25 |
| 后端 | 2C2G | ¥60-80 |
| 前端 | 1C512M | ¥30-40 |
| **总计** | | **¥135-195/月** |

> 提示：学生用户可申请 Sealos 优惠额度

---

## 📞 技术支持

- Sealos 官方文档：https://sealos.io/docs/
- Sealos 社区：https://github.com/labring/sealos
- 项目 Issues：提交到您的代码仓库

---

**祝您部署顺利！🎊**
