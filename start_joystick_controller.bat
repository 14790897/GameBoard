@echo off
echo ========================================
echo    JoystickController Launcher
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to PATH
    pause
    exit /b 1
)

echo 🐍 Python detected
echo 🔤 Switching to English input method...
echo 🎮 Starting JoystickController...
echo.

REM Start the Python program
python joystick_controller_final.py

REM If the program exits, show a message
echo.
echo 🛑 JoystickController stopped
pause
