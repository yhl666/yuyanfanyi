@echo off
chcp 65001 >nul
echo ========================================
echo Whisper 语音识别测试工具
echo ========================================
echo.

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 启动测试程序...
echo.

python test_whisper_simple.py

pause
