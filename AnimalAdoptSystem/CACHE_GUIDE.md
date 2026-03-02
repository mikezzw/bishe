# 缓存系统使用指南

## 系统概述

本系统集成了Redis缓存，提供了多层次的缓存策略来提升系统性能。

## 技术架构

- **缓存后端**: Redis (生产环境) / LocMemCache (开发环境)
- **缓存库**: django-redis
- **缓存层级**: 应用层缓存 + 数据库查询缓存
- **失效策略**: 时间过期 + 主动清除

## 缓存配置

### 缓存键命名规范
```
animals:list:           # 动物列表缓存
animals:detail:{id}     # 动物详情缓存
shelters:list:          # 基地列表缓存
shelters:detail:{id}    # 基地详情缓存
posts:list:             # 帖子列表缓存
posts:detail:{id}       # 帖子详情缓存
users:profile:{id}      # 用户资料缓存
stats:                  # 统计数据缓存
```

### 缓存时间策略
```python
CACHE_TIMEOUT = {
    'short': 300,        # 5分钟 - 频繁变动数据
    'medium': 1800,      # 30分钟 - 中等频率更新数据
    'long': 7200,        # 2小时 - 较少变动数据
    'very_long': 86400,  # 24小时 - 很少变动数据
}
```

## 使用方法

### 1. 函数级别缓存
```python
from utils.cache_utils import cache_result, CACHE_TIMEOUT

@cache_result('long', 'animals:list:')
def get_animal_list():
    # 获取动物列表的业务逻辑
    return Animal.objects.all()
```

### 2. 视图级别缓存
```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from utils.cache_utils import CACHE_TIMEOUT

@method_decorator(cache_page(CACHE_TIMEOUT['long']), name='list')
class AnimalViewSet(viewsets.ModelViewSet):
    # ViewSet实现
    pass
```

### 3. 手动缓存操作
```python
from django.core.cache import cache
from utils.cache_utils import get_cache_key

# 设置缓存
cache_key = get_cache_key('animals:list:', page, size)
cache.set(cache_key, data, timeout=3600)

# 获取缓存
cached_data = cache.get(cache_key)

# 删除缓存
cache.delete(cache_key)
```

## 缓存管理API

### 1. 查看缓存状态
```
GET /api/cache/status/
```

### 2. 清空缓存
```
POST /api/cache/clear/
{
    "type": "all"  // all, animals, shelters, posts, users
}
```

### 3. 获取统计信息
```
GET /api/cache/stats/
```

## 缓存失效策略

### 自动失效
- 基于时间的过期策略
- Redis内存淘汰策略

### 主动清除
- 数据更新时自动清除相关缓存
- 手动清除特定类型缓存
- 系统维护时批量清除

### 缓存穿透防护
```python
# 对于查询结果为空的情况也进行缓存
if not result:
    cache.set(cache_key, [], timeout=CACHE_TIMEOUT['short'])
```

## 性能监控

### 缓存命中率监控
```python
import logging
logger = logging.getLogger(__name__)

def cached_function():
    cache_key = "some:key"
    result = cache.get(cache_key)
    if result is not None:
        logger.debug(f"缓存命中: {cache_key}")
        return result
    # ... 执行原逻辑
```

### 缓存大小监控
定期检查Redis内存使用情况和缓存键数量。

## 最佳实践

1. **合理设置缓存时间**
   - 高频读低频写数据设置较长缓存时间
   - 高频写数据设置较短缓存时间

2. **缓存键设计**
   - 使用有意义的前缀
   - 包含版本信息便于升级
   - 避免过长的键名

3. **内存管理**
   - 定期清理过期缓存
   - 监控内存使用情况
   - 设置合理的最大内存限制

4. **异常处理**
   - 缓存服务不可用时降级到直接查询数据库
   - 记录缓存相关错误日志

## 部署注意事项

### 开发环境
使用本地内存缓存，无需安装Redis

### 生产环境
1. 安装并配置Redis服务
2. 设置适当的内存限制
3. 配置持久化策略
4. 设置监控告警

### Docker部署
```dockerfile
# docker-compose.yml
redis:
  image: redis:alpine
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data
```

## 故障排除

### 常见问题
1. **缓存连接失败**: 检查Redis服务状态和网络连接
2. **缓存击穿**: 使用互斥锁或设置空值缓存
3. **内存不足**: 调整缓存策略或增加Redis内存

### 调试技巧
```python
# 启用详细日志
LOGGING = {
    'loggers': {
        'django.core.cache': {
            'level': 'DEBUG',
        }
    }
}
```