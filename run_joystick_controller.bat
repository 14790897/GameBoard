@echo off
echo ========================================
echo    JoystickController - Game Version
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

echo Starting JoystickController...
echo.

REM Change to the directory where the batch file is located
cd /d "%~dp0"

REM Run the executable
JoystickController_Release\JoystickController.exe

echo.
echo JoystickController has exited.
pause
