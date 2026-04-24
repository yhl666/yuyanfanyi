@echo off
echo ========================================
echo BabelBridge 后端服务启动脚本
echo ========================================
echo.

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 启动服务器...
echo 访问地址: http://localhost:8000
echo 按 Ctrl+C 停止服务器
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000
