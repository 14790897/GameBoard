@echo off
chcp 65001 >nul
echo ========================================
echo    JoystickController - 游戏手柄控制器
echo ========================================
echo.
echo 正在启动手柄控制器...
echo.

REM Change to the directory where the batch file is located
cd /d "%~dp0"

REM Run the executable
JoystickController.exe

echo.
echo 手柄控制器已退出。
pause
