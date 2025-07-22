@echo off
chcp 65001 >nul
echo ========================================
echo    JoystickController - 游戏手柄控制器
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

echo 正在启动手柄控制器...
echo.

REM Change to the directory where the batch file is located
cd /d "%~dp0"

REM Run the executable
JoystickController.exe

echo.
echo 手柄控制器已退出。
pause
