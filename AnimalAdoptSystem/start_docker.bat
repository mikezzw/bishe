@echo off
chcp 65001 >nul
echo ========================================
echo   动物领养系统 - Docker 快速启动脚本
echo ========================================
echo.

echo [1/4] 检查 Docker 是否安装...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker 已安装
echo.

echo [2/4] 检查 Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose 未安装
    pause
    exit /b 1
)
echo ✅ Docker Compose 已安装
echo.

echo [3/4] 构建并启动服务（首次运行可能需要几分钟）...
docker-compose up --build -d

if errorlevel 1 (
    echo ❌ 启动失败，请检查错误信息
    pause
    exit /b 1
)
echo ✅ 服务启动成功
echo.

echo [4/4] 等待服务就绪...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   🎉 部署完成！
echo ========================================
echo.
echo 📱 访问地址：
echo   前端页面: http://localhost
echo   后端 API: http://localhost:8000/api/
echo   Admin后台: http://localhost:8000/admin/
echo.
echo 📊 查看日志: docker-compose logs -f
echo 🛑 停止服务: docker-compose down
echo.
echo ========================================
pause
