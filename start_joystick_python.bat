@echo off
echo ========================================
echo   JoystickController - Python Version
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as administrator - Best compatibility
    echo.
) else (
    echo ⚠️  NOT running as administrator
    echo.
    echo 🎯 For best game compatibility, it's recommended to run as administrator:
    echo    1. Right-click this batch file
    echo    2. Select "Run as administrator"
    echo.
    echo 📝 Some games may not respond properly without admin rights.
    echo    You can continue anyway, but if you experience issues,
    echo    please restart with administrator privileges.
    echo.
    echo Press any key to continue anyway, or Ctrl+C to exit...
    pause >nul
    echo.
)

echo Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ first:
    echo 1. Download from https://python.org
    echo 2. Make sure to check "Add Python to PATH" during installation
    echo 3. Restart this script
    echo.
    pause
    exit /b 1
)

echo ✅ Python environment OK
echo.

echo Checking dependencies...
python -c "import serial, win32api, keyboard" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Some dependencies are missing
    echo.
    echo Would you like to install them automatically? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo.
        echo Installing dependencies...
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        echo.
        if %errorlevel% equ 0 (
            echo ✅ Dependencies installed successfully!
        ) else (
            echo ❌ Failed to install dependencies
            echo Please run: pip install -r requirements.txt
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Please install dependencies manually:
        echo   pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo ✅ All dependencies OK
echo.

REM Change to the directory where the batch file is located
cd /d "%~dp0"

echo Starting JoystickController (Python version)...
echo.
echo 🎮 Press Ctrl+C to stop the program
echo.

REM Run the Python script
python joystick_controller_final.py

echo.
echo JoystickController has exited.
pause
