@echo off
echo ========================================
echo JoystickShield PC Controller 安装脚本
echo ========================================

echo.
echo 正在检查 Python...
python --version
if errorlevel 1 (
    echo ❌ 未找到 Python! 请先安装 Python 3.7+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖库...
echo.

echo 安装 pyserial (串口通信)...
pip install pyserial

echo.
echo 安装 keyboard (键盘模拟)...
pip install keyboard

echo.
echo ========================================
echo ✅ 安装完成！
echo ========================================
echo.
echo 使用方法:
echo 1. 将 Arduino 连接到电脑
echo 2. 上传 JoystickShield 代码到 Arduino  
echo 3. 运行: python joystick_controller.py
echo.
echo 注意: 需要以管理员身份运行 (keyboard 库要求)
echo.
pause
