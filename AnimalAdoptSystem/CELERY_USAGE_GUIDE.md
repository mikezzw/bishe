# Celery 异步任务使用指南

## 简介
本项目已成功集成 Celery 异步任务处理系统，用于处理耗时操作，如发送邮件、图像识别、定时任务等。

## 已安装的组件
- **Celery 5.3.6**: 异步任务队列
- **Redis 5.0.1**: 消息代理和结果存储
- **相关依赖**: 已添加到 requirements.txt

## 目录结构
```
AnimalAdoptSystem/
├── backend/
│   ├── celery.py          # Celery 主配置文件
│   ├── __init__.py        # 确保 Celery 应用被加载
│   └── settings.py        # 已添加 Celery 配置
├── users/
│   └── tasks.py           # 用户相关异步任务
├── notifications/
│   └── tasks.py           # 通知相关任务
├── reports/
│   └── tasks.py           # 报告生成任务
├── utils/
│   └── tasks.py           # 工具类任务
├── start_celery_worker.bat   # 启动 Worker 脚本
└── start_celery_beat.bat     # 启动定时任务脚本
```

## 配置说明

### Django Settings 配置
已在 `backend/settings.py` 中添加：
```python
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
```

## 可用的异步任务

### 用户模块 (users/tasks.py)
1. **send_welcome_email(user_id)** - 发送欢迎邮件
2. **send_adoption_status_update(user_id, adoption_id, status)** - 发送领养状态更新
3. **cleanup_inactive_users()** - 清理未激活用户

### 通知模块 (notifications/tasks.py)
1. **cleanup_expired_notifications()** - 清理过期通知
2. **send_daily_summary()** - 发送每日摘要邮件

### 报告模块 (reports/tasks.py)
1. **generate_daily_report()** - 生成每日运营报告
2. **backup_database()** - 数据库备份
3. **send_weekly_statistics()** - 发送每周统计报告

### 工具模块 (utils/tasks.py)
1. **clear_cache()** - 清理缓存
2. **health_check()** - 系统健康检查
3. **process_image_analysis(image_data, analysis_type)** - 图像分析

## 使用方法

### 1. 启动前准备
确保 Redis 服务器正在运行：
```bash
# Windows (如果已安装 Redis)
redis-server

# 或者使用 Docker
docker run -d -p 6379:6379 redis:latest
```

### 2. 启动 Celery Worker
```bash
# 方法一：使用启动脚本
start_celery_worker.bat

# 方法二：手动启动
cd AnimalAdoptSystem
celery -A backend worker --loglevel=info
```

### 3. 启动 Celery Beat (定时任务)
```bash
# 方法一：使用启动脚本
start_celery_beat.bat

# 方法二：手动启动
cd AnimalAdoptSystem
celery -A backend beat --loglevel=info
```

### 4. 在代码中调用任务
```python
# 异步执行（推荐）
from users.tasks import send_welcome_email
result = send_welcome_email.delay(user_id=123)

# 同步执行（等待结果）
result = send_welcome_email.apply_async(args=[123], countdown=10)

# 获取任务结果
print(result.get(timeout=10))
```

## 开发新的任务

### 1. 创建任务文件
在相应的 Django app 目录下创建 `tasks.py` 文件：

```python
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def my_new_task(param1, param2):
    """任务描述"""
    try:
        # 任务逻辑
        result = do_something(param1, param2)
        logger.info(f'任务执行成功: {result}')
        return result
    except Exception as e:
        logger.error(f'任务执行失败: {str(e)}')
        raise
```

### 2. 任务最佳实践
- 使用 `shared_task` 装饰器而不是 `app.task`
- 添加适当的日志记录
- 处理异常情况
- 返回有意义的结果
- 避免长时间阻塞操作

## 监控和调试

### 查看任务状态
```python
# 在 Django shell 中
from celery.result import AsyncResult
result = AsyncResult('task_id')
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)  # 任务返回值或异常
```

### 查看 Worker 状态
```bash
# 查看活跃的 Worker
celery -A backend inspect active

# 查看统计信息
celery -A backend inspect stats
```

## 常见问题解决

### 1. Redis 连接失败
- 确保 Redis 服务正在运行
- 检查防火墙设置
- 验证 Redis 配置是否正确

### 2. 任务执行失败
- 查看 Worker 日志输出
- 检查任务函数是否有语法错误
- 确认依赖项是否正确安装

### 3. 任务重复执行
- 检查是否多个 Worker 在运行
- 确认任务的唯一性约束

## 性能优化建议

1. **合理设置并发数**：根据服务器性能调整 worker 数量
2. **任务优先级**：为重要任务设置更高优先级
3. **结果存储**：对于不需要结果的任务，设置 `ignore_result=True`
4. **任务超时**：设置合理的任务超时时间
5. **内存管理**：定期重启 worker 避免内存泄漏

## 安全注意事项

1. **敏感信息**：不要在任务参数中传递密码等敏感信息
2. **权限控制**：确保任务只能被授权用户触发
3. **输入验证**：对任务参数进行适当验证
4. **错误处理**：妥善处理任务执行中的异常情况