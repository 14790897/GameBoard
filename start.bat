@echo off
title JoystickShield 游戏控制器

echo ========================================
echo 🎮 JoystickShield 游戏控制器启动器
echo ========================================
echo.

echo 请选择控制器版本:
echo 1. 基础版 (joystick_controller.py)
echo 2. 增强版 (advanced_controller.py)
echo.

set /p choice="请输入选择 (1-2): "

if "%choice%"=="1" (
    echo.
    echo 🚀 启动基础版控制器...
    python joystick_controller.py
) else if "%choice%"=="2" (
    echo.
    echo 🚀 启动增强版控制器...
    python advanced_controller.py
) else (
    echo.
    echo ❌ 无效选择，默认启动增强版...
    python advanced_controller.py
)

echo.
pause
