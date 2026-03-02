@echo off
echo 正在启动 Celery Beat (定时任务调度器)...
echo 请确保 Redis 服务器正在运行 (redis-server)
echo.

cd /d D:\Code\python\AnimalAdoptSystem\AnimalAdoptSystem

echo 启动 Celery Beat...
celery -A backend beat --loglevel=info

pause