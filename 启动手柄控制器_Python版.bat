@echo off
chcp 65001 >nul
echo ========================================
echo   JoystickController - Python 版本
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 正在以管理员身份运行 - 最佳兼容性
    echo.
) else (
    echo ⚠️  未以管理员身份运行
    echo.
    echo 🎯 为获得最佳游戏兼容性，建议以管理员身份运行：
    echo    1. 右键点击此批处理文件
    echo    2. 选择"以管理员身份运行"
    echo.
    echo 📝 某些游戏在没有管理员权限时可能无法正常响应。
    echo    您可以继续运行，但如果遇到问题，
    echo    请重新以管理员权限启动。
    echo.
    echo 按任意键继续运行，或按 Ctrl+C 退出...
    pause >nul
    echo.
)

echo 正在检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo.
    echo 请先安装Python 3.7+：
    echo 1. 从 https://python.org 下载
    echo 2. 安装时确保勾选"Add Python to PATH"
    echo 3. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo ✅ Python环境正常
echo.

echo 正在检查依赖包...
python -c "import serial, win32api, keyboard" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  缺少某些依赖包
    echo.
    echo 是否自动安装依赖包？(Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo.
        echo 正在安装依赖包...
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        echo.
        if %errorlevel% equ 0 (
            echo ✅ 依赖包安装成功！
        ) else (
            echo ❌ 依赖包安装失败
            echo 请手动运行：pip install -r requirements.txt
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo 请手动安装依赖包：
        echo   pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo ✅ 所有依赖包正常
echo.

REM Change to the directory where the batch file is located
cd /d "%~dp0"

echo 正在启动手柄控制器 (Python版本)...
echo.
echo 🎮 按 Ctrl+C 停止程序
echo.

REM Run the Python script
python joystick_controller_final.py

echo.
echo 手柄控制器已退出。
pause
