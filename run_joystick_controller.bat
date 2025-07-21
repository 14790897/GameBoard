@echo off
echo ========================================
echo    JoystickController - Game Version
echo ========================================
echo.
echo Starting JoystickController...
echo.

REM Change to the directory where the batch file is located
cd /d "%~dp0"

REM Run the executable
dist\JoystickController.exe

echo.
echo JoystickController has exited.
pause
