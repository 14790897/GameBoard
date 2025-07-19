#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 COM13 优先逻辑
"""

import serial
import serial.tools.list_ports
import time

def test_com13_priority():
    """测试 COM13 优先连接逻辑"""
    print("🧪 测试 COM13 优先连接逻辑")
    print("-" * 40)
    
    # 首先尝试 COM13
    preferred_port = "COM13"
    print(f"🔍 尝试连接 {preferred_port}...")
    
    try:
        test_serial = serial.Serial(preferred_port, 115200, timeout=1)
        test_serial.close()
        print(f"✅ {preferred_port} 可用！")
        return preferred_port
    except Exception as e:
        print(f"⚠️  {preferred_port} 不可用: {e}")
        print("📡 搜索其他可用串口...")
    
    # 列出所有可用串口
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ 没有找到任何串口")
        return None
    
    print("\n可用串口列表:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
        
        # 测试每个端口
        try:
            test_serial = serial.Serial(port.device, 115200, timeout=0.5)
            test_serial.close()
            print(f"    ✅ {port.device} 测试成功")
        except Exception as e:
            print(f"    ❌ {port.device} 测试失败: {e}")
    
    return None

def test_arduino_detection():
    """测试 Arduino 设备自动识别"""
    print("\n🎯 测试 Arduino 设备自动识别")
    print("-" * 40)
    
    ports = serial.tools.list_ports.comports()
    arduino_keywords = ["arduino", "ch340", "cp2102", "ftdi", "usb"]
    
    found_arduino = False
    for port in ports:
        for keyword in arduino_keywords:
            if keyword in port.description.lower():
                print(f"🎯 疑似 Arduino 设备: {port.device}")
                print(f"   描述: {port.description}")
                found_arduino = True
                break
    
    if not found_arduino:
        print("🔍 未找到明显的 Arduino 设备标识")

if __name__ == "__main__":
    print("🚀 COM13 优先逻辑测试工具")
    print("=" * 50)
    
    try:
        test_com13_priority()
        test_arduino_detection()
        
        print("\n" + "=" * 50)
        print("✨ 测试完成！")
        print("💡 如果 COM13 可用，控制器将优先使用它")
        print("💡 如果 COM13 不可用，将自动检测其他串口")
        
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
    
    input("\n按回车键退出...")
