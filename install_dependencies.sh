#!/bin/bash

echo "========================================"
echo "  JoystickController - Dependency Setup"
echo "========================================"
echo

echo "Checking Python environment..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3 not found"
    echo "Please install Python 3.7+ first"
    exit 1
fi

echo
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

echo
echo "Installing core dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo
    echo "✅ Dependencies installed successfully!"
    echo
    echo "Installed packages:"
    echo "- pyserial (serial communication)"
    echo "- keyboard (keyboard control)"
    echo "- pyinstaller (packaging tool)"
    echo
    echo "Note: pywin32 is Windows-only and will be skipped on this platform"
    echo
    echo "You can now run the program:"
    echo "  python3 joystick_controller_final.py"
    echo
    echo "Or rebuild the executable:"
    echo "  pyinstaller joystick_controller.spec"
else
    echo "❌ Dependency installation failed"
    echo "Please check your network connection and Python environment"
fi

echo
read -p "Press Enter to continue..."
