#!/usr/bin/env python3
"""
JoystickShield PC 控制器
监听 Arduino 串口数据并模拟键盘输入
"""

import serial
import serial.tools.list_ports
import keyboard
import time
import threading
import sys
from collections import defaultdict

class JoystickController:
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.key_states = defaultdict(bool)  # 记录按键状态，避免重复触发
        
        # 按键映射配置
        self.key_mapping = {
            # 摇杆方向 -> 键盘按键
            "摇杆：上": "w",
            "摇杆：下": "s", 
            "摇杆：左": "a",
            "摇杆：右": "d",
            "摇杆：左上": ["w", "a"],
            "摇杆：右上": ["w", "d"],
            "摇杆：左下": ["s", "a"],
            "摇杆：右下": ["s", "d"],
            
            # 按钮 -> 键盘按键
            "摇杆按键按下": "space",
            "上按钮按下": "up",
            "下按钮按下": "down", 
            "左按钮按下": "left",
            "右按钮按下": "right",
            "E 按钮按下": "e",
            "F 按钮按下": "f",
            
            # 特殊功能
            "摇杆偏离中心": None,  # 不映射按键
        }
        
    def find_arduino_port(self):
        """查找 Arduino 串口，优先使用 COM13"""
        # 首先尝试 COM13
        preferred_port = "COM13"
        try:
            test_serial = serial.Serial(preferred_port, 115200, timeout=1)
            test_serial.close()
            print(f"✅ 优先使用串口: {preferred_port}")
            return preferred_port
        except Exception:
            print(f"⚠️  {preferred_port} 不可用，自动检测其他串口...")
        
        ports = serial.tools.list_ports.comports()
        
        print("可用串口:")
        for i, port in enumerate(ports):
            print(f"{i+1}. {port.device} - {port.description}")
        
        if not ports:
            print("❌ 没有找到可用串口！")
            return None
            
        # 尝试自动识别 Arduino
        for port in ports:
            if "arduino" in port.description.lower() or "ch340" in port.description.lower():
                print(f"🎯 自动识别到 Arduino: {port.device}")
                return port.device
                
        # 手动选择
        try:
            choice = input(f"请选择串口 (1-{len(ports)}): ")
            index = int(choice) - 1
            if 0 <= index < len(ports):
                return ports[index].device
        except ValueError:
            pass
            
        return None
    
    def connect_serial(self, port=None, baudrate=115200):
        """连接串口"""
        if port is None:
            # 直接使用 COM13 端口
            port = "COM13"
            
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
            print(f"✅ 串口连接成功: {port} @ {baudrate}")
            time.sleep(2)  # 等待 Arduino 重启
            return True
        except Exception as e:
            print(f"❌ 串口连接失败: {e}")
            # 如果 COM13 连接失败，尝试自动查找
            if port == "COM13":
                print("🔍 COM13 连接失败，尝试自动查找...")
                port = self.find_arduino_port()
                if port:
                    try:
                        self.serial_port = serial.Serial(port, baudrate, timeout=1)
                        print(f"✅ 串口连接成功: {port} @ {baudrate}")
                        time.sleep(2)
                        return True
                    except Exception as e2:
                        print(f"❌ 备用串口连接失败: {e2}")
            return False
    
    def press_keys(self, keys):
        """按下按键"""
        if isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            if not self.key_states[key]:
                keyboard.press(key)
                self.key_states[key] = True
                print(f"🔽 按下: {key}")
    
    def release_keys(self, keys):
        """释放按键"""
        if isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            if self.key_states[key]:
                keyboard.release(key)
                self.key_states[key] = False
                print(f"🔼 释放: {key}")
    
    def release_all_keys(self):
        """释放所有按键"""
        for key, pressed in self.key_states.items():
            if pressed:
                keyboard.release(key)
                self.key_states[key] = False
    
    def process_joystick_data(self, data):
        """处理摇杆数据"""
        data = data.strip()
        
        # 解析带时间戳的数据格式: "16:18:54.901 > 摇杆：下"
        if " > " in data:
            timestamp, actual_data = data.split(" > ", 1)
            data = actual_data.strip()
        
        # 忽略校准和系统信息
        ignore_patterns = ["校准", "测试程序", "开始检测", "=", "正在", "完成"]
        if any(pattern in data for pattern in ignore_patterns):
            return
        
        # 处理位置数据 - 检测摇杆回中
        if "摇杆位置" in data:
            self.handle_position_data(data)
            return
            
        print(f"📡 接收: {data}")
        
        # 检查是否是已映射的动作
        if data in self.key_mapping:
            keys = self.key_mapping[data]
            if keys:
                self.press_keys(keys)
    
    def handle_position_data(self, data):
        """处理位置数据"""
        try:
            # 解析 "摇杆位置 -> X: -3, Y: -96" 格式
            if "X:" in data and "Y:" in data:
                # 更稳健的解析方法
                # 找到 "X:" 和 "Y:" 的位置
                x_start = data.find("X:") + 2
                comma_pos = data.find(",", x_start)
                y_start = data.find("Y:") + 2
                
                x_str = data[x_start:comma_pos].strip()
                y_str = data[y_start:].strip()
                
                x_pos = int(x_str)
                y_pos = int(y_str)
                
                # 检测摇杆回中 (死区范围 ±10)
                if abs(x_pos) <= 10 and abs(y_pos) <= 10:
                    # 释放所有方向键
                    direction_keys = ["w", "a", "s", "d"]
                    for key in direction_keys:
                        if self.key_states[key]:
                            self.release_keys(key)
                    print(f"🎯 摇杆回中: X={x_pos}, Y={y_pos}")
                else:
                    print(f"📍 摇杆位置: X={x_pos}, Y={y_pos}")
                    
        except Exception as e:
            print(f"⚠️  位置数据解析错误: {e}")
            print(f"原始数据: {data}")
    
    def serial_listener(self):
        """串口监听线程"""
        print("🎮 开始监听摇杆数据...")
        
        while self.is_running:
            try:
                if self.serial_port and self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode('utf-8', errors='ignore')
                    if data:
                        self.process_joystick_data(data)
                        
            except Exception as e:
                print(f"❌ 串口读取错误: {e}")
                break
                
            time.sleep(0.01)  # 10ms 轮询间隔
    
    def start(self):
        """启动控制器"""
        print("=" * 50)
        print("🎮 JoystickShield PC 控制器")
        print("=" * 50)
        
        # 连接串口
        if not self.connect_serial():
            return
        
        # 显示按键映射
        print("\n🎯 按键映射:")
        for action, keys in self.key_mapping.items():
            if keys:
                if isinstance(keys, list):
                    keys_str = " + ".join(keys)
                else:
                    keys_str = keys
                print(f"  {action} -> {keys_str}")
        
        print(f"\n⌨️  按 Ctrl+C 退出")
        print("-" * 50)
        
        # 启动监听线程
        self.is_running = True
        listener_thread = threading.Thread(target=self.serial_listener)
        listener_thread.daemon = True
        listener_thread.start()
        
        try:
            # 主循环
            while True:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 正在退出...")
            self.stop()
    
    def stop(self):
        """停止控制器"""
        self.is_running = False
        self.release_all_keys()
        
        if self.serial_port:
            self.serial_port.close()
            print("✅ 串口已关闭")
        
        print("✅ 控制器已停止")

def main():
    # 检查依赖
    try:
        import serial
        import keyboard
    except ImportError as e:
        print("❌ 缺少依赖库，请安装:")
        print("pip install pyserial keyboard")
        sys.exit(1)
    
    # 创建并启动控制器
    controller = JoystickController()
    controller.start()

if __name__ == "__main__":
    main()
