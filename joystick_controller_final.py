#!/usr/bin/env python3
"""
JoystickShield PC 控制器 - 最终游戏版本
专门针对游戏优化，确保按键能被正确识别
"""

import serial
import serial.tools.list_ports
import time
import threading
import sys
import ctypes
from collections import defaultdict

# 导入输入库
try:
    import win32api
    import win32con
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

class GameJoystickController:
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.key_states = defaultdict(bool)
        self.last_position = {"x": 0, "y": 0}

        # 长按功能相关
        self.button_press_times = {}  # 记录按键按下的时间
        self.button_states = {}  # 记录按键状态
        self.long_press_threshold = 0.5  # 长按阈值（秒）
        self.long_press_triggered = {}  # 记录是否已触发长按

        # 方向键自动释放相关
        self.last_direction_time = {}  # 记录最后一次方向键触发时间
        self.direction_timeout = 0.2  # 方向键超时时间（秒）
        
        # 使用最兼容的输入方法
        self.use_win32 = WIN32_AVAILABLE
        
        # Windows 虚拟键码映射
        self.vk_codes = {
            'w': 0x57, 'a': 0x41, 's': 0x53, 'd': 0x44,
            'v': 0x56, 'space': 0x20, 'e': 0x45, 'f': 0x46,
            'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
            'o': 0x4F, 'j': 0x4A, 'i': 0x49, 'k': 0x4B,  # 基本按键
            'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12  # 修饰键
        }
        
        # 按键映射配置
        self.key_mapping = {
            # 摇杆方向 -> 键盘按键 (与按钮映射保持一致)
            "摇杆：上": "w",      # 对应上按钮
            "摇杆：下": "s",      # 对应下按钮
            "摇杆：左": "a",      # 对应左按钮
            "摇杆：右": "d",      # 对应右按钮
            "摇杆：左上": ["a", "w"],    # 上+左
            "摇杆：右上": ["d", "w"],    # 上+右
            "摇杆：左下": ["a", "s"],    # 下+左
            "摇杆：右下": ["d", "s"],    # 下+右

            # 按钮 -> 键盘按键（短按）
            "摇杆按键按下": "f",
            "上按钮按下": "o",
            "下按钮按下": "j",
            "左按钮按下": "i",
            "右按钮按下": "k",
            "E 按钮按下": "e",
            "F 按钮按下": "v",

            # 特殊功能
            "摇杆偏离中心": None,  # 不映射按键
        }

        # 长按映射配置
        self.long_press_mapping = {
            "摇杆按键": "space",  # 长按摇杆按键 -> 空格
            "上按钮": "up",       # 长按上按钮 -> 上方向键
            "下按钮": "down",     # 长按下按钮 -> 下方向键
            "左按钮": "left",     # 长按左按钮 -> 左方向键
            "右按钮": "right",    # 长按右按钮 -> 右方向键
            "E 按钮": "shift",    # 长按E按钮 -> Shift
            "F 按钮": "ctrl",     # 长按F按钮 -> Ctrl
        }
    
    def get_foreground_window_title(self):
        """获取当前活动窗口标题"""
        if not WIN32_AVAILABLE:
            return "Unknown"
        try:
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
        except:
            return "Unknown"
    
    def ensure_game_focus(self):
        """确保游戏窗口获得焦点"""
        window_title = self.get_foreground_window_title()
        if "python" in window_title.lower() or "cmd" in window_title.lower():
            print(f"⚠️  当前活动窗口: {window_title}")
            print("请切换到游戏窗口！")
            return False
        return True
    
    def press_key_win32(self, key):
        """使用 Win32 API 按下按键"""
        if not self.use_win32 or key not in self.vk_codes:
            return False
        
        try:
            # 确保游戏窗口处于活动状态
            if not self.ensure_game_focus():
                return False
            
            vk_code = self.vk_codes[key]
            win32api.keybd_event(vk_code, 0, 0, 0)
            return True
        except Exception as e:
            print(f"❌ Win32 按键失败 {key}: {e}")
            return False
    
    def release_key_win32(self, key):
        """使用 Win32 API 释放按键"""
        if not self.use_win32 or key not in self.vk_codes:
            return False
        
        try:
            vk_code = self.vk_codes[key]
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            print(f"❌ Win32 释放失败 {key}: {e}")
            return False
    
    def press_key_keyboard(self, key):
        """使用 keyboard 库按下按键"""
        if not KEYBOARD_AVAILABLE:
            return False
        try:
            keyboard.press(key)
            return True
        except Exception as e:
            print(f"❌ keyboard 按键失败 {key}: {e}")
            return False
    
    def release_key_keyboard(self, key):
        """使用 keyboard 库释放按键"""
        if not KEYBOARD_AVAILABLE:
            return False
        try:
            keyboard.release(key)
            return True
        except Exception as e:
            print(f"❌ keyboard 释放失败 {key}: {e}")
            return False
    
    def press_keys_continuous(self, keys):
        """按下按键（持续状态）"""
        if isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            if not self.key_states[key]:
                success = False
                
                # 优先使用 Win32 API
                if self.use_win32:
                    success = self.press_key_win32(key)
                    method = "Win32"
                else:
                    success = self.press_key_keyboard(key)
                    method = "keyboard"
                
                # 如果首选方法失败，尝试备用方法
                if not success:
                    if self.use_win32 and KEYBOARD_AVAILABLE:
                        success = self.press_key_keyboard(key)
                        method = "keyboard(备用)"
                    elif not self.use_win32 and WIN32_AVAILABLE:
                        success = self.press_key_win32(key)
                        method = "Win32(备用)"
                
                if success:
                    self.key_states[key] = True
                    print(f"🔽 按下: {key} ({method})")
                else:
                    print(f"❌ 无法按下按键: {key}")
    
    def press_keys(self, keys):
        """按下按键（按钮事件）"""
        if isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            success_press = False
            success_release = False
            method = ""
            
            # 按下
            if self.use_win32:
                success_press = self.press_key_win32(key)
                method = "Win32"
            else:
                success_press = self.press_key_keyboard(key)
                method = "keyboard"
            
            if success_press:
                print(f"🔽 按下: {key} ({method})")
                time.sleep(0.05)  # 短暂延迟
                
                # 释放
                if self.use_win32:
                    success_release = self.release_key_win32(key)
                else:
                    success_release = self.release_key_keyboard(key)
                
                if success_release:
                    print(f"🔼 释放: {key} ({method})")
                else:
                    print(f"❌ 无法释放按键: {key}")
            else:
                print(f"❌ 无法按下按键: {key}")
    
    def release_keys(self, keys):
        """释放按键"""
        if isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            if self.key_states[key]:
                success = False
                method = ""
                
                if self.use_win32:
                    success = self.release_key_win32(key)
                    method = "Win32"
                else:
                    success = self.release_key_keyboard(key)
                    method = "keyboard"
                
                if success:
                    self.key_states[key] = False
                    print(f"🔼 释放: {key} ({method})")
                else:
                    print(f"❌ 无法释放按键: {key}")
    
    def release_all_keys(self):
        """释放所有按键"""
        for key, pressed in self.key_states.items():
            if pressed:
                if self.use_win32:
                    self.release_key_win32(key)
                else:
                    self.release_key_keyboard(key)
                self.key_states[key] = False

    def handle_button_press(self, button_name):
        """处理按钮按下事件"""
        current_time = time.time()

        # 记录按下时间
        self.button_press_times[button_name] = current_time
        self.button_states[button_name] = True
        self.long_press_triggered[button_name] = False

        print(f"🔽 按钮按下: {button_name}")

    def handle_button_release(self, button_name):
        """处理按钮释放事件"""
        if button_name not in self.button_states or not self.button_states[button_name]:
            return

        current_time = time.time()
        press_time = self.button_press_times.get(button_name, current_time)
        hold_duration = current_time - press_time

        self.button_states[button_name] = False

        # 如果已经触发了长按，只需要释放长按键
        if self.long_press_triggered.get(button_name, False):
            long_press_key = self.long_press_mapping.get(button_name)
            if long_press_key:
                self.release_single_key(long_press_key)
                print(f"🔼 长按释放: {button_name} -> {long_press_key} (持续 {hold_duration:.2f}s)")
        else:
            # 短按：执行短按动作
            short_press_action = f"{button_name}按下"
            if short_press_action in self.key_mapping:
                keys = self.key_mapping[short_press_action]
                if keys:
                    self.press_keys(keys)
                    print(f"👆 短按: {button_name} -> {keys} (持续 {hold_duration:.2f}s)")

    def check_long_press(self):
        """检查是否有按键达到长按条件"""
        current_time = time.time()

        for button_name, is_pressed in self.button_states.items():
            if not is_pressed:
                continue

            press_time = self.button_press_times.get(button_name, current_time)
            hold_duration = current_time - press_time

            # 如果达到长按阈值且还未触发长按
            if hold_duration >= self.long_press_threshold and not self.long_press_triggered.get(button_name, False):
                self.long_press_triggered[button_name] = True

                # 触发长按动作
                long_press_key = self.long_press_mapping.get(button_name)
                if long_press_key:
                    self.press_single_key_continuous(long_press_key)
                    print(f"🔽 长按触发: {button_name} -> {long_press_key} (持续 {hold_duration:.2f}s)")

    def press_single_key_continuous(self, key):
        """按下单个按键（持续状态）"""
        if not self.key_states[key]:
            success = False
            method = ""

            if self.use_win32:
                success = self.press_key_win32(key)
                method = "Win32"
            else:
                success = self.press_key_keyboard(key)
                method = "keyboard"

            if success:
                self.key_states[key] = True
                print(f"🔽 按下: {key} ({method})")

    def release_single_key(self, key):
        """释放单个按键"""
        if self.key_states[key]:
            success = False
            method = ""

            if self.use_win32:
                success = self.release_key_win32(key)
                method = "Win32"
            else:
                success = self.release_key_keyboard(key)
                method = "keyboard"

            if success:
                self.key_states[key] = False
                print(f"🔼 释放: {key} ({method})")

    def press_direction_keys(self, keys, direction_data):
        """处理方向键按下（短按模式）"""
        if isinstance(keys, str):
            keys = [keys]

        current_time = time.time()

        # 记录方向键触发时间
        for key in keys:
            self.last_direction_time[key] = current_time

        # 执行短按
        self.press_keys(keys)
        print(f"🎮 方向短按: {direction_data} -> {'+'.join(keys)}")

    def release_all_direction_keys(self):
        """释放所有方向键"""
        direction_keys = ["w", "a", "s", "d"]
        released_keys = []

        for key in direction_keys:
            if self.key_states[key]:
                self.release_single_key(key)
                released_keys.append(key)

        if released_keys:
            print(f"🎯 摇杆回中，释放方向键: {'+'.join(released_keys)}")

    def check_direction_timeout(self):
        """检查方向键是否超时，如果超时则释放"""
        current_time = time.time()
        direction_keys = ["w", "a", "s", "d"]

        for key in direction_keys:
            if key in self.last_direction_time:
                time_since_last = current_time - self.last_direction_time[key]
                if time_since_last > self.direction_timeout:
                    # 超时，释放按键
                    if self.key_states[key]:
                        self.release_single_key(key)
                        print(f"⏰ 方向键超时释放: {key}")
                    # 清除记录
                    del self.last_direction_time[key]
    
    def connect_serial(self, baudrate=115200):
        """连接串口 - 自动查找可用端口"""
        return self.auto_find_port(baudrate)
    
    def auto_find_port(self, baudrate=115200):
        """自动查找Arduino端口"""
        print("🔍 自动查找Arduino端口...")
        ports = serial.tools.list_ports.comports()

        if not ports:
            print("❌ 没有找到任何串口设备")
            return False

        print(f"发现 {len(ports)} 个串口设备:")
        for i, port in enumerate(ports, 1):
            print(f"  {i}. {port.device} - {port.description}")

        # 优先尝试包含 Arduino 关键词的端口
        arduino_ports = []
        other_ports = []

        for port in ports:
            description = port.description.lower()
            if any(keyword in description for keyword in ['arduino', 'ch340', 'ch341', 'cp210', 'ftdi']):
                arduino_ports.append(port)
            else:
                other_ports.append(port)

        # 先尝试 Arduino 相关端口，然后尝试其他端口
        all_ports = arduino_ports + other_ports

        for port in all_ports:
            try:
                print(f"🔌 尝试连接: {port.device} ({port.description})")
                self.serial_port = serial.Serial(port.device, baudrate, timeout=1)
                print(f"✅ 成功连接到: {port.device}")
                time.sleep(2)  # 等待Arduino重启
                return True
            except Exception as e:
                print(f"   ❌ 连接失败: {e}")
                continue

        print("❌ 所有端口都无法连接")
        return False
    
    def process_joystick_data(self, data):
        """处理摇杆数据"""
        data = data.strip()
        
        # 解析带时间戳的数据
        if " > " in data:
            _, actual_data = data.split(" > ", 1)
            data = actual_data.strip()
        
        # 忽略系统信息
        ignore_patterns = ["校准", "测试程序", "开始检测", "=", "正在", "完成"]
        if any(pattern in data for pattern in ignore_patterns):
            return
        
        # 处理位置数据
        if "摇杆位置" in data:
            self.handle_position_data(data)
            return
            
        print(f"📡 接收: {data}")

        # 处理按钮按下事件（支持长按）
        if "按下" in data:
            button_name = data.replace("按下", "").strip()
            self.handle_button_press(button_name)
            return

        # 处理按钮释放事件
        if "释放" in data:
            button_name = data.replace("释放", "").strip()
            self.handle_button_release(button_name)
            return

        # 处理摇杆回中事件
        if "摇杆偏离中心" in data or "摇杆回中" in data:
            self.release_all_direction_keys()
            return

        # 检查摇杆方向映射
        if data in self.key_mapping:
            keys = self.key_mapping[data]
            if keys:
                # 摇杆方向使用持续按键（长按）
                if "摇杆：" in data:
                    self.press_keys_continuous(keys)  # 持续按住方向键
                    print(f"🎮 摇杆方向: {data} -> 持续按住 {'+'.join(keys) if isinstance(keys, list) else keys}")
                else:
                    self.press_keys_continuous(keys)  # 其他事件
    
    def handle_position_data(self, data):
        """处理位置数据"""
        try:
            if "X:" in data and "Y:" in data:
                x_start = data.find("X:") + 2
                comma_pos = data.find(",", x_start)
                y_start = data.find("Y:") + 2
                
                if comma_pos == -1:
                    return
                
                x_str = data[x_start:comma_pos].strip()
                y_str = data[y_start:].strip()
                
                x_pos = int(x_str)
                y_pos = int(y_str)
                
                # 死区检测
                dead_zone = 10
                if abs(x_pos) <= dead_zone and abs(y_pos) <= dead_zone:
                    # 释放所有方向键
                    direction_keys = ["w", "a", "s", "d"]
                    for key in direction_keys:
                        if self.key_states[key]:
                            self.release_keys(key)
                    print(f"🎯 摇杆回中: X={x_pos}, Y={y_pos}")
                else:
                    # 处理方向移动
                    self.handle_movement(x_pos, y_pos, dead_zone)
                    
        except Exception as e:
            print(f"⚠️  位置数据解析错误: {e}")
    
    def handle_movement(self, x_pos, y_pos, dead_zone):
        """处理移动"""
        # 先释放所有方向键
        direction_keys = ["w", "a", "s", "d"]
        for key in direction_keys:
            if self.key_states[key]:
                self.release_keys(key)
        
        # 确定需要按下的键
        keys_to_press = []
        
        if y_pos > dead_zone:  # 向上（Y轴正值表示向上）
            keys_to_press.append("w")
        elif y_pos < -dead_zone:  # 向下（Y轴负值表示向下）
            keys_to_press.append("s")
            
        if x_pos < -dead_zone:  # 向左
            keys_to_press.append("a")
        elif x_pos > dead_zone:  # 向右
            keys_to_press.append("d")
        
        # 按下相应的键
        if keys_to_press:
            self.press_keys_continuous(keys_to_press)
            print(f"🎮 移动: {'+'.join(keys_to_press)} (X={x_pos}, Y={y_pos})")
    
    def serial_listener(self):
        """串口监听线程"""
        print("🎮 开始监听摇杆数据...")

        while self.is_running:
            try:
                # 处理串口数据
                if self.serial_port and self.serial_port.is_open and self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode('utf-8', errors='ignore')
                    if data:
                        self.process_joystick_data(data)

                # 检查长按状态
                self.check_long_press()

                # 检查方向键超时
                self.check_direction_timeout()

            except Exception as e:
                print(f"❌ 串口读取错误: {e}")
                break

            time.sleep(0.01)
    
    def start(self):
        """启动控制器"""
        print("=" * 60)
        print("🎮 JoystickController - 最终游戏版本")
        print("=" * 60)
        
        # 显示输入方法
        method = "Win32 API" if self.use_win32 else "keyboard 库"
        print(f"🎯 输入方法: {method}")
        
        # 检查权限
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin:
                print("✅ 以管理员身份运行")
            else:
                print("⚠️  未以管理员身份运行，可能影响游戏兼容性")
        except:
            pass
        
        # 连接串口
        if not self.connect_serial():
            print("❌ 无法连接串口，程序退出")
            return
        
        # 显示按键映射
        print("\n🎯 摇杆方向映射:")
        direction_actions = [k for k in self.key_mapping.keys() if "摇杆：" in k]
        for action in direction_actions:
            keys = self.key_mapping[action]
            if keys:
                if isinstance(keys, list):
                    keys_str = " + ".join(keys)
                else:
                    keys_str = keys
                print(f"  {action} -> {keys_str}")

        print("\n🎯 按钮短按映射:")
        button_actions = [k for k in self.key_mapping.keys() if "按下" in k]
        for action in button_actions:
            keys = self.key_mapping[action]
            if keys:
                if isinstance(keys, list):
                    keys_str = " + ".join(keys)
                else:
                    keys_str = keys
                print(f"  {action} -> {keys_str}")

        print(f"\n🎯 按钮长按映射 (长按 {self.long_press_threshold}s 触发):")
        for button_name, long_key in self.long_press_mapping.items():
            print(f"  {button_name}长按 -> {long_key}")

        print(f"\n⚠️  重要提示:")
        print("1. 请确保游戏窗口处于活动状态")
        print("2. 建议将游戏设置为窗口化模式")
        print("3. 支持按钮短按和长按功能")
        print("4. 如果仍无响应，请检查游戏输入设置")
        print("\n⌨️  按 Ctrl+C 退出")
        print("-" * 60)
        
        # 启动监听线程
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
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("✅ 串口已关闭")
        
        print("✅ 控制器已停止")

def main():
    print("🔍 检查依赖库...")
    
    if not WIN32_AVAILABLE and not KEYBOARD_AVAILABLE:
        print("❌ 缺少输入库，请安装:")
        print("pip install pywin32 keyboard")
        sys.exit(1)
    
    if WIN32_AVAILABLE:
        print("✅ Win32 API 可用")
    if KEYBOARD_AVAILABLE:
        print("✅ keyboard 库可用")
    
    controller = GameJoystickController()
    controller.start()

if __name__ == "__main__":
    main()
