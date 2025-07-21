@echo off
echo ========================================
echo   JoystickController - 依赖安装脚本
echo ========================================
echo.

echo 正在检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.7+
    pause
    exit /b 1
)

echo.
echo 正在升级pip...
python -m pip install --upgrade pip

echo.
echo 正在安装核心依赖...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ✅ 依赖安装成功！
    echo.
    echo 已安装的包:
    echo - pyserial (串口通信)
    echo - pywin32 (Windows API)
    echo - keyboard (键盘控制)
    echo - pyinstaller (打包工具)
    echo.
    echo 现在可以运行程序:
    echo   python joystick_controller_final.py
    echo.
    echo 或者重新构建可执行文件:
    echo   pyinstaller joystick_controller.spec
) else (
    echo ❌ 依赖安装失败
    echo 请检查网络连接和Python环境
)

echo.
pause
