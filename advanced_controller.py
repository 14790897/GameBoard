#!/usr/bin/env python3
"""
JoystickShield 游戏控制器 - 增强版
支持多种游戏模式和高级功能
"""

import serial
import serial.tools.list_ports
import keyboard
import time
import threading
import sys
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

@dataclass
class GameProfile:
    """游戏配置文件"""
    name: str
    key_mapping: Dict[str, Union[str, List[str]]]
    description: str = ""

class AdvancedJoystickController:
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.key_states = defaultdict(bool)
        self.current_profile = 0
        self.last_position = {"x": 0, "y": 0}
        
        # 定义游戏配置文件
        self.game_profiles = [
            GameProfile(
                name="FPS 游戏 (WASD + 鼠标)",
                key_mapping={
                    "摇杆：上": "w", "摇杆：下": "s", "摇杆：左": "a", "摇杆：右": "d",
                    "摇杆：左上": ["w", "a"], "摇杆：右上": ["w", "d"],
                    "摇杆：左下": ["s", "a"], "摇杆：右下": ["s", "d"],
                    "摇杆按键按下": "space", "上按钮按下": "r", "下按钮按下": "c",
                    "左按钮按下": "shift", "右按钮按下": "ctrl", 
                    "E 按钮按下": "e", "F 按钮按下": "f"
                },
                description="适用于 CS:GO, Valorant 等 FPS 游戏"
            ),
            GameProfile(
                name="方向键模式",
                key_mapping={
                    "摇杆：上": "up", "摇杆：下": "down", "摇杆：左": "left", "摇杆：右": "right",
                    "摇杆按键按下": "enter", "上按钮按下": "w", "下按钮按下": "s",
                    "左按钮按下": "a", "右按钮按下": "d",
                    "E 按钮按下": "esc", "F 按钮按下": "tab"
                },
                description="适用于老式游戏和应用导航"
            ),
            GameProfile(
                name="多媒体控制",
                key_mapping={
                    "摇杆：上": "volume up", "摇杆：下": "volume down",
                    "摇杆：左": "previous track", "摇杆：右": "next track",
                    "摇杆按键按下": "play/pause media", 
                    "E 按钮按下": "volume mute", "F 按钮按下": "stop media"
                },
                description="控制音乐播放和音量"
            ),
            GameProfile(
                name="自定义模式",
                key_mapping={
                    "摇杆：上": "i", "摇杆：下": "k", "摇杆：左": "j", "摇杆：右": "l",
                    "摇杆按键按下": "space", "上按钮按下": "u", "下按钮按下": "o",
                    "E 按钮按下": "1", "F 按钮按下": "2"
                },
                description="可自定义的按键映射"
            )
        ]
    
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
        
        print("🔍 搜索可用串口:")
        for i, port in enumerate(ports):
            print(f"  {i+1}. {port.device} - {port.description}")
        
        if not ports:
            print("❌ 没有找到可用串口！")
            return None
        
        # 尝试自动识别 Arduino
        arduino_keywords = ["arduino", "ch340", "cp2102", "ftdi"]
        for port in ports:
            for keyword in arduino_keywords:
                if keyword in port.description.lower():
                    print(f"🎯 自动识别到 Arduino: {port.device}")
                    return port.device
        
        # 手动选择
        try:
            choice = input(f"\n请选择串口 (1-{len(ports)}) 或按回车自动选择: ")
            if not choice:
                return ports[0].device
            index = int(choice) - 1
            if 0 <= index < len(ports):
                return ports[index].device
        except ValueError:
            pass
        
        return None
    
    def connect_serial(self, port=None, baudrate=115200):
        """连接串口"""
        if port is None:
            port = self.find_arduino_port()
        
        if port is None:
            return False
        
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
            print(f"✅ 串口连接成功: {port} @ {baudrate}")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"❌ 串口连接失败: {e}")
            return False
    
    def switch_profile(self):
        """切换游戏配置"""
        self.current_profile = (self.current_profile + 1) % len(self.game_profiles)
        profile = self.game_profiles[self.current_profile]
        print(f"\n🎮 切换到: {profile.name}")
        print(f"📝 描述: {profile.description}")
        self.release_all_keys()
    
    def press_keys(self, keys):
        """按下按键"""
        if keys is None:
            return
            
        if isinstance(keys, str):
            keys = [keys]
        
        for key in keys:
            if not self.key_states[key]:
                try:
                    keyboard.press(key)
                    self.key_states[key] = True
                    print(f"🔽 {key}")
                except Exception as e:
                    print(f"❌ 按键错误 {key}: {e}")
    
    def release_keys(self, keys):
        """释放按键"""
        if keys is None:
            return
            
        if isinstance(keys, str):
            keys = [keys]
        
        for key in keys:
            if self.key_states[key]:
                try:
                    keyboard.release(key)
                    self.key_states[key] = False
                    print(f"🔼 {key}")
                except Exception as e:
                    print(f"❌ 释放按键错误 {key}: {e}")
    
    def release_all_keys(self):
        """释放所有按键"""
        for key in list(self.key_states.keys()):
            if self.key_states[key]:
                try:
                    keyboard.release(key)
                    self.key_states[key] = False
                except:
                    pass
    
    def process_position_data(self, data):
        """处理位置数据"""
        try:
            # 解析 "摇杆位置 -> X: -3, Y: -96" 格式
            if "X:" in data and "Y:" in data:
                parts = data.split("X:")[1].split(",")
                x_str = parts[0].strip()
                y_str = parts[1].split("Y:")[1].strip()
                
                x_pos = int(x_str)
                y_pos = int(y_str)
                
                # 先检测摇杆是否在死区内 (死区范围 ±10)
                if abs(x_pos) <= 10 and abs(y_pos) <= 10:
                    if self.last_position["x"] != 0 or self.last_position["y"] != 0:
                        # 释放所有方向键
                        profile = self.game_profiles[self.current_profile]
                        direction_actions = ["摇杆：上", "摇杆：下", "摇杆：左", "摇杆：右"]
                        for action in direction_actions:
                            if action in profile.key_mapping:
                                self.release_keys(profile.key_mapping[action])
                        print(f"🎯 摇杆回中: X={x_pos}, Y={y_pos}")
                else:
                    # 只有不在死区时才根据位置数据触发移动
                    self.handle_movement_from_position(x_pos, y_pos)
                
                # 更新位置记录
                self.last_position = {"x": x_pos, "y": y_pos}
                
                # 只在大幅度移动时显示位置
                if abs(x_pos) > 20 or abs(y_pos) > 20:
                    print(f"📍 摇杆位置: X={x_pos}, Y={y_pos}")
                    
        except Exception as e:
            print(f"⚠️  位置数据解析错误: {e}")
    
    def handle_movement_from_position(self, x_pos, y_pos):
        """根据摇杆位置触发移动"""
        # 死区范围
        dead_zone = 10
        
        # 双重检查：确保不在死区内
        if abs(x_pos) <= dead_zone and abs(y_pos) <= dead_zone:
            # 如果在死区内，只释放按键，不触发新按键
            profile = self.game_profiles[self.current_profile]
            direction_actions = ["摇杆：上", "摇杆：下", "摇杆：左", "摇杆：右"]
            for action in direction_actions:
                if action in profile.key_mapping:
                    keys = profile.key_mapping[action]
                    if isinstance(keys, str):
                        keys = [keys]
                    for key in keys:
                        if self.key_states[key]:
                            self.release_keys(key)
            print(f"🎯 摇杆在死区内，释放所有方向键: X={x_pos}, Y={y_pos}")
            return
        
        # 获取当前配置
        profile = self.game_profiles[self.current_profile]
        
        # 先释放所有方向键
        direction_actions = ["摇杆：上", "摇杆：下", "摇杆：左", "摇杆：右"]
        for action in direction_actions:
            if action in profile.key_mapping:
                keys = profile.key_mapping[action]
                if isinstance(keys, str):
                    keys = [keys]
                for key in keys:
                    if self.key_states[key]:
                        self.release_keys(key)
        
        # 根据位置确定需要触发的动作
        actions_to_trigger = []
        
        # 垂直方向 (Y轴)
        if y_pos < -dead_zone:  # 向上
            actions_to_trigger.append("摇杆：上")
        elif y_pos > dead_zone:  # 向下
            actions_to_trigger.append("摇杆：下")
            
        # 水平方向 (X轴)
        if x_pos < -dead_zone:  # 向左
            actions_to_trigger.append("摇杆：左")
        elif x_pos > dead_zone:  # 向右
            actions_to_trigger.append("摇杆：右")
        
        # 触发相应的动作
        if actions_to_trigger:
            all_keys = []
            for action in actions_to_trigger:
                if action in profile.key_mapping:
                    keys = profile.key_mapping[action]
                    if isinstance(keys, str):
                        all_keys.append(keys)
                    elif isinstance(keys, list):
                        all_keys.extend(keys)
            
            # 去重并按下键
            unique_keys = list(set(all_keys))
            if unique_keys:
                self.press_keys(unique_keys)
                
                # 显示移动信息
                direction_str = ""
                if "摇杆：上" in actions_to_trigger and "摇杆：左" in actions_to_trigger:
                    direction_str = "左上"
                elif "摇杆：上" in actions_to_trigger and "摇杆：右" in actions_to_trigger:
                    direction_str = "右上"
                elif "摇杆：下" in actions_to_trigger and "摇杆：左" in actions_to_trigger:
                    direction_str = "左下"
                elif "摇杆：下" in actions_to_trigger and "摇杆：右" in actions_to_trigger:
                    direction_str = "右下"
                elif "摇杆：上" in actions_to_trigger:
                    direction_str = "上"
                elif "摇杆：下" in actions_to_trigger:
                    direction_str = "下"
                elif "摇杆：左" in actions_to_trigger:
                    direction_str = "左"
                elif "摇杆：右" in actions_to_trigger:
                    direction_str = "右"
                
                print(f"🎮 摇杆移动: {direction_str} ({'+'.join(unique_keys)}) [{self.current_profile}模式]")
        else:
            print(f"🤔 位置计算异常: X={x_pos}, Y={y_pos} (应该在死区外但没有按键触发)")
    
    def process_joystick_data(self, data):
        """处理摇杆数据"""
        data = data.strip()
        
        # 解析带时间戳的数据格式: "16:18:54.901 > 摇杆：下"
        if " > " in data:
            timestamp, actual_data = data.split(" > ", 1)
            data = actual_data.strip()
        
        # 处理位置数据
        if "摇杆位置" in data:
            self.handle_position_data(data)
            return
        
        # 忽略其他非操作数据
        ignore_patterns = ["校准", "测试程序", "开始检测", "=", "正在", "完成"]
        if any(pattern in data for pattern in ignore_patterns):
            return
        
        # 获取当前配置
        profile = self.game_profiles[self.current_profile]
        
        print(f"📡 {data}")
        
        # 处理映射动作
        if data in profile.key_mapping:
            keys = profile.key_mapping[data]
            self.press_keys(keys)
    
    def handle_position_data(self, data):
        """处理位置数据 (别名方法)"""
        self.process_position_data(data)
    
    def serial_listener(self):
        """串口监听线程"""
        print("🎮 开始监听摇杆数据...\n")
        
        while self.is_running:
            try:
                if self.serial_port and self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode('utf-8', errors='ignore')
                    if data.strip():
                        self.process_joystick_data(data)
                        
            except Exception as e:
                print(f"❌ 串口读取错误: {e}")
                break
            
            time.sleep(0.01)
    
    def setup_hotkeys(self):
        """设置热键"""
        try:
            keyboard.add_hotkey('ctrl+shift+p', self.switch_profile)
            print("🔥 热键已设置: Ctrl+Shift+P = 切换配置")
        except Exception as e:
            print(f"⚠️  热键设置失败: {e}")
    
    def show_profiles(self):
        """显示所有配置文件"""
        print("\n🎮 可用游戏配置:")
        for i, profile in enumerate(self.game_profiles):
            marker = "👉" if i == self.current_profile else "  "
            print(f"{marker} {i+1}. {profile.name}")
            print(f"     {profile.description}")
        print()
    
    def show_current_mapping(self):
        """显示当前按键映射"""
        profile = self.game_profiles[self.current_profile]
        print(f"\n🎯 当前配置: {profile.name}")
        print("按键映射:")
        for action, keys in profile.key_mapping.items():
            if keys:
                if isinstance(keys, list):
                    keys_str = " + ".join(keys)
                else:
                    keys_str = keys
                print(f"  {action} -> {keys_str}")
        print()
    
    def start(self):
        """启动控制器"""
        print("=" * 60)
        print("🎮 JoystickShield 游戏控制器 - 增强版")
        print("=" * 60)
        
        # 连接串口
        if not self.connect_serial():
            return
        
        # 设置热键
        self.setup_hotkeys()
        
        # 显示配置
        self.show_profiles()
        self.show_current_mapping()
        
        print("📋 控制说明:")
        print("  • Ctrl+Shift+P: 切换游戏配置")
        print("  • Ctrl+C: 退出程序")
        print("-" * 60)
        
        # 启动监听
        self.is_running = True
        listener_thread = threading.Thread(target=self.serial_listener)
        listener_thread.daemon = True
        listener_thread.start()
        
        try:
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
    # 检查管理员权限
    try:
        keyboard.press('f24')  # 测试按键
        keyboard.release('f24')
    except Exception:
        print("❌ 需要管理员权限来模拟按键！")
        print("请以管理员身份运行此程序")
        input("按回车键退出...")
        sys.exit(1)
    
    # 检查依赖
    try:
        import serial
        import keyboard
    except ImportError:
        print("❌ 缺少依赖库，请运行 install.bat 安装")
        input("按回车键退出...")
        sys.exit(1)
    
    # 启动控制器
    controller = AdvancedJoystickController()
    controller.start()

if __name__ == "__main__":
    main()
