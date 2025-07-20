#!/usr/bin/env python3
"""
依赖安装脚本
自动安装 JoystickController 所需的所有依赖库
"""

import subprocess
import sys
import importlib.util

def check_package(package_name):
    """检查包是否已安装"""
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name):
    """安装包"""
    try:
        print(f"正在安装 {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package_name} 安装失败: {e}")
        return False

def main():
    print("=" * 50)
    print("🔧 JoystickController 依赖安装工具")
    print("=" * 50)
    
    # 基本依赖（必需）
    basic_deps = [
        ("serial", "pyserial"),  # (import_name, package_name)
        ("keyboard", "keyboard")
    ]
    
    # 可选依赖（提高兼容性）
    optional_deps = [
        ("pynput", "pynput"),
        ("win32api", "pywin32")
    ]
    
    print("\n📦 检查基本依赖...")
    basic_missing = []
    for import_name, package_name in basic_deps:
        if check_package(import_name):
            print(f"✅ {package_name} 已安装")
        else:
            print(f"❌ {package_name} 未安装")
            basic_missing.append(package_name)
    
    print("\n📦 检查可选依赖...")
    optional_missing = []
    for import_name, package_name in optional_deps:
        if check_package(import_name):
            print(f"✅ {package_name} 已安装")
        else:
            print(f"⚠️  {package_name} 未安装（可选）")
            optional_missing.append(package_name)
    
    # 安装缺失的基本依赖
    if basic_missing:
        print(f"\n🔧 安装基本依赖: {', '.join(basic_missing)}")
        for package in basic_missing:
            if not install_package(package):
                print(f"❌ 基本依赖 {package} 安装失败，程序可能无法正常运行")
                return False
    
    # 询问是否安装可选依赖
    if optional_missing:
        print(f"\n🤔 发现可选依赖未安装: {', '.join(optional_missing)}")
        print("这些库可以提高游戏兼容性，建议安装。")
        
        choice = input("是否安装可选依赖？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            for package in optional_missing:
                install_package(package)
        else:
            print("⚠️  跳过可选依赖安装")
    
    print("\n" + "=" * 50)
    print("🎉 依赖检查完成！")
    
    # 最终检查
    print("\n📋 最终状态:")
    all_good = True
    
    for import_name, package_name in basic_deps:
        if check_package(import_name):
            print(f"✅ {package_name}")
        else:
            print(f"❌ {package_name}")
            all_good = False
    
    for import_name, package_name in optional_deps:
        if check_package(import_name):
            print(f"✅ {package_name} (可选)")
        else:
            print(f"⚠️  {package_name} (可选)")
    
    if all_good:
        print("\n🚀 所有基本依赖已就绪，可以运行 joystick_controller.py")
    else:
        print("\n❌ 部分基本依赖缺失，请手动安装")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
