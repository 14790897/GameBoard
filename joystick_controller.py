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

# 尝试导入额外的输入库
try:
    import pynput.keyboard as pynput_kb
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

class JoystickController:
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.key_states = defaultdict(bool)  # 记录按键状态，避免重复触发
        self.last_position = {"x": 0, "y": 0}  # 记录上一次摇杆位置
        self.position_history = []  # 位置历史记录
        self.max_history = 3  # 保留最近几次位置记录

        # 按键模拟方法选择
        self.input_method = "keyboard"  # 默认使用 keyboard 库
        self.pynput_controller = None

        # 初始化 pynput 控制器（如果可用）
        if PYNPUT_AVAILABLE:
            try:
                self.pynput_controller = pynput_kb.Controller()
                print("✅ pynput 库可用，可作为备用输入方法")
            except Exception as e:
                print(f"⚠️  pynput 初始化失败: {e}")

        # Windows 虚拟键码映射
        self.vk_codes = {
            'w': 0x57, 'a': 0x41, 's': 0x53, 'd': 0x44,
            'space': 0x20, 'e': 0x45, 'f': 0x46,
            'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27
        }
        self.button_states = defaultdict(bool)  # 记录按钮状态，避免重复触发
        self.last_button_time = defaultdict(float)  # 记录按钮最后触发时间
        self.button_debounce_time = 0.1  # 按钮防抖时间（100ms）
        
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

            # 按钮 -> 键盘按键
            "摇杆按键按下": "v",
            "上按钮按下": "o",      
            "下按钮按下": "j",    
            "左按钮按下": "i",   
            "右按钮按下": "k",  
            "E 按钮按下": "e",
            "F 按钮按下": "f",
            
            # 特殊功能
            "摇杆偏离中心": None,  
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
    
    def _press_key_keyboard(self, key):
        """使用 keyboard 库按下按键"""
        try:
            keyboard.press(key)
            return True
        except Exception as e:
            print(f"❌ keyboard 库按键失败 {key}: {e}")
            return False

    def _release_key_keyboard(self, key):
        """使用 keyboard 库释放按键"""
        try:
            keyboard.release(key)
            return True
        except Exception as e:
            print(f"❌ keyboard 库释放失败 {key}: {e}")
            return False

    def _press_key_pynput(self, key):
        """使用 pynput 库按下按键"""
        if not self.pynput_controller:
            return False
        try:
            if key in ['up', 'down', 'left', 'right']:
                # 方向键需要特殊处理
                key_map = {
                    'up': pynput_kb.Key.up,
                    'down': pynput_kb.Key.down,
                    'left': pynput_kb.Key.left,
                    'right': pynput_kb.Key.right
                }
                self.pynput_controller.press(key_map[key])
            elif key == 'space':
                self.pynput_controller.press(pynput_kb.Key.space)
            else:
                self.pynput_controller.press(key)
            return True
        except Exception as e:
            print(f"❌ pynput 库按键失败 {key}: {e}")
            return False

    def _release_key_pynput(self, key):
        """使用 pynput 库释放按键"""
        if not self.pynput_controller:
            return False
        try:
            if key in ['up', 'down', 'left', 'right']:
                key_map = {
                    'up': pynput_kb.Key.up,
                    'down': pynput_kb.Key.down,
                    'left': pynput_kb.Key.left,
                    'right': pynput_kb.Key.right
                }
                self.pynput_controller.release(key_map[key])
            elif key == 'space':
                self.pynput_controller.release(pynput_kb.Key.space)
            else:
                self.pynput_controller.release(key)
            return True
        except Exception as e:
            print(f"❌ pynput 库释放失败 {key}: {e}")
            return False

    def _press_key_win32(self, key):
        """使用 Win32 API 按下按键"""
        if not WIN32_AVAILABLE or key not in self.vk_codes:
            return False
        try:
            vk_code = self.vk_codes[key]
            win32api.keybd_event(vk_code, 0, 0, 0)  # 按下
            return True
        except Exception as e:
            print(f"❌ Win32 API 按键失败 {key}: {e}")
            return False

    def _release_key_win32(self, key):
        """使用 Win32 API 释放按键"""
        if not WIN32_AVAILABLE or key not in self.vk_codes:
            return False
        try:
            vk_code = self.vk_codes[key]
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
            return True
        except Exception as e:
            print(f"❌ Win32 API 释放失败 {key}: {e}")
            return False

    def press_keys_continuous(self, keys):
        """按下按键（针对摇杆方向，持续状态）"""
        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            if not self.key_states[key]:
                success = False

                # 尝试多种按键方法
                if self.input_method == "keyboard":
                    success = self._press_key_keyboard(key)

                if not success and PYNPUT_AVAILABLE:
                    print(f"🔄 尝试使用 pynput 按下 {key}")
                    success = self._press_key_pynput(key)

                if not success and WIN32_AVAILABLE:
                    print(f"🔄 尝试使用 Win32 API 按下 {key}")
                    success = self._press_key_win32(key)

                if success:
                    self.key_states[key] = True
                    print(f"🔽 按下: {key}")
                else:
                    print(f"❌ 所有方法都无法按下按键: {key}")

    def press_keys(self, keys):
        """按下按键（针对按钮事件，执行按下-释放）"""
        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            # 对于按钮事件，执行完整的按下-释放动作
            success_press = False
            success_release = False

            # 尝试按下
            if self.input_method == "keyboard":
                success_press = self._press_key_keyboard(key)

            if not success_press and PYNPUT_AVAILABLE:
                success_press = self._press_key_pynput(key)

            if not success_press and WIN32_AVAILABLE:
                success_press = self._press_key_win32(key)

            if success_press:
                print(f"🔽 按下: {key}")
                time.sleep(0.05)  # 短暂延迟确保按键被识别

                # 尝试释放
                if self.input_method == "keyboard":
                    success_release = self._release_key_keyboard(key)

                if not success_release and PYNPUT_AVAILABLE:
                    success_release = self._release_key_pynput(key)

                if not success_release and WIN32_AVAILABLE:
                    success_release = self._release_key_win32(key)

                if success_release:
                    print(f"🔼 释放: {key}")
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

                # 尝试多种释放方法
                if self.input_method == "keyboard":
                    success = self._release_key_keyboard(key)

                if not success and PYNPUT_AVAILABLE:
                    success = self._release_key_pynput(key)

                if not success and WIN32_AVAILABLE:
                    success = self._release_key_win32(key)

                if success:
                    self.key_states[key] = False
                    print(f"🔼 释放: {key}")
                else:
                    print(f"❌ 无法释放按键: {key}")

    def release_all_keys(self):
        """释放所有按键"""
        for key, pressed in self.key_states.items():
            if pressed:
                self.release_keys(key)
    
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
        # if "摇杆位置" in data:
        #     self.handle_position_data(data)
        #     return
            
        print(f"📡 接收: {data}")
        
        # 检查是否是按钮事件（需要防抖处理）
        if "按钮按下" in data or "按键按下" in data:
            if self.should_process_button_event(data):
                # 检查是否是已映射的动作
                if data in self.key_mapping:
                    keys = self.key_mapping[data]
                    if keys:
                        self.press_keys(keys)  # 按钮事件用瞬时按压
                        # 记录按钮状态和时间
                        self.button_states[data] = True
                        self.last_button_time[data] = time.time()
            else:
                print(f"🚫 按钮防抖: {data} (忽略重复触发)")
        else:
            # 摇杆方向事件 - 每次都触发一次按下-释放
            if data in self.key_mapping:
                keys = self.key_mapping[data]
                if keys:
                    self.press_keys(keys)  # 每次都按下-释放
    
    def should_process_button_event(self, button_data):
        """判断是否应该处理按钮事件（防抖）"""
        current_time = time.time()
        last_time = self.last_button_time.get(button_data, 0)
        
        # 如果距离上次触发的时间超过防抖时间，则允许处理
        return current_time - last_time > self.button_debounce_time
    
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

                # 检查解析位置是否有效
                if comma_pos == -1 or x_start < 2 or y_start < 2:
                    print(f"⚠️  位置数据格式异常: {data}")
                    return

                x_str = data[x_start:comma_pos].strip()
                y_str = data[y_start:].strip()

                # 移除可能的非数字字符
                x_str = ''.join(c for c in x_str if c.isdigit() or c in '+-')
                y_str = ''.join(c for c in y_str if c.isdigit() or c in '+-')

                if not x_str or not y_str:
                    print(f"⚠️  无法提取有效数字: X='{x_str}', Y='{y_str}'")
                    return

                x_pos = int(x_str)
                y_pos = int(y_str)

                # 数值范围检查 (Arduino 摇杆通常在 -512 到 512 范围内)
                if abs(x_pos) > 1000 or abs(y_pos) > 1000:
                    print(f"⚠️  位置数值超出合理范围: X={x_pos}, Y={y_pos}")
                    return

                # 检查位置是否有变化，避免重复处理相同位置
                if (self.last_position["x"] == x_pos and 
                    self.last_position["y"] == y_pos):
                    return  # 位置没有变化，直接返回

                # 更新位置历史
                self.update_position_history(x_pos, y_pos)

                # 先检测摇杆是否在死区内 (死区范围调整为适合-100~100的范围)
                dead_zone_threshold = 15  # 与handle_movement_from_position保持一致
                if abs(x_pos) <= dead_zone_threshold and abs(y_pos) <= dead_zone_threshold:
                    # 释放所有方向键
                    direction_keys = ["w", "a", "s", "d"]  # 使用正确的摇杆方向键
                    for key in direction_keys:
                        if self.key_states[key]:
                            self.release_keys(key)
                    print(f"🎯 摇杆回中: X={x_pos}, Y={y_pos}")
                else:
                    # 直接处理移动，移除复杂的回中检测逻辑
                    self.handle_movement_from_position(x_pos, y_pos)
                    print(f"📍 摇杆位置: X={x_pos}, Y={y_pos}")

                # 更新最后位置
                self.last_position = {"x": x_pos, "y": y_pos}

        except ValueError as e:
            print(f"⚠️  数值转换错误: {e}")
            print(f"原始数据: {data}")
        except Exception as e:
            print(f"⚠️  位置数据解析错误: {e}")
            print(f"原始数据: {data}")
    
    def update_position_history(self, x_pos, y_pos):
        """更新位置历史记录"""
        self.position_history.append({"x": x_pos, "y": y_pos})
        
        # 保持历史记录数量不超过最大值
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)
    
    def handle_movement_from_position(self, x_pos, y_pos):
        """根据摇杆位置触发移动"""
        # 死区范围 - 根据摇杆坐标范围(-100~100)调整死区
        dead_zone = 15  # 适合-100~100范围的死区
        
        # 添加调试信息
        print(f"🔍 调试: 摇杆位置 X={x_pos}, Y={y_pos}, 死区={dead_zone}")
        
        # 双重检查：确保不在死区内
        if abs(x_pos) <= dead_zone and abs(y_pos) <= dead_zone:
            # 如果在死区内，释放所有方向键
            direction_keys = ["w", "a", "s", "d"]  # 更新为新的方向键
            keys_to_release = [key for key in direction_keys if self.key_states[key]]
            
            if keys_to_release:
                for key in keys_to_release:
                    self.release_keys(key)
                print(f"🎯 摇杆在死区内，释放所有方向键: X={x_pos}, Y={y_pos}")
            return
        
        # 根据位置确定需要按下的键（简化逻辑）
        keys_to_press = []
        
        # 垂直方向 (Y轴)
        if y_pos < -dead_zone:  # 向上
            keys_to_press.append("w")
            print(f"🔍 Y轴: 向上触发 (y_pos={y_pos} < -{dead_zone})")
        elif y_pos > dead_zone:  # 向下
            keys_to_press.append("s")
            print(f"🔍 Y轴: 向下触发 (y_pos={y_pos} > {dead_zone})")

        # 水平方向 (X轴)
        if x_pos < -dead_zone:  # 向左
            keys_to_press.append("a")
            print(f"🔍 X轴: 向左触发 (x_pos={x_pos} < -{dead_zone})")
        elif x_pos > dead_zone:  # 向右
            keys_to_press.append("d")
            print(f"🔍 X轴: 向右触发 (x_pos={x_pos} > {dead_zone})")

        # 智能按键管理：只改变有差异的按键状态
        direction_keys = ["w", "a", "s", "d"]  # 更新为新的方向键：上w 左a 下s 右d
        keys_to_press_set = set(keys_to_press)
        currently_pressed_set = set(key for key in direction_keys if self.key_states[key])
        
        print(f"🔍 按键状态: 应按下={keys_to_press}, 当前按下={list(currently_pressed_set)}")
        
        # 需要释放的键（当前按下但不应该按下的）
        keys_to_release = currently_pressed_set - keys_to_press_set
        for key in keys_to_release:
            self.release_keys(key)
            
        # 需要按下的键（应该按下但当前没按下的）
        keys_to_press_new = keys_to_press_set - currently_pressed_set
        for key in keys_to_press_new:
            self.press_keys_continuous([key])
        
        # 只在有按键变化时输出日志
        if keys_to_release or keys_to_press_new:
            if keys_to_press:
                direction_str = ""
                if "w" in keys_to_press and "a" in keys_to_press:
                    direction_str = "左上"
                elif "w" in keys_to_press and "d" in keys_to_press:
                    direction_str = "右上"
                elif "s" in keys_to_press and "a" in keys_to_press:
                    direction_str = "左下"
                elif "s" in keys_to_press and "d" in keys_to_press:
                    direction_str = "右下"
                elif "w" in keys_to_press:
                    direction_str = "上"
                elif "s" in keys_to_press:
                    direction_str = "下"
                elif "a" in keys_to_press:
                    direction_str = "左"
                elif "d" in keys_to_press:
                    direction_str = "右"
                
                print(f"🎮 摇杆移动: {direction_str} ({'+'.join(keys_to_press)})")
            else:
                print("🎯 摇杆回中，释放所有方向键")
    
    def serial_listener(self):
        """串口监听线程"""
        print("🎮 开始监听摇杆数据...")

        while self.is_running:
            try:
                if self.serial_port and self.serial_port.is_open and self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode('utf-8', errors='ignore')
                    if data:
                        self.process_joystick_data(data)

            except serial.SerialException as e:
                print(f"❌ 串口连接错误: {e}")
                print("🔄 尝试重新连接...")
                self.reconnect_serial()

            except Exception as e:
                print(f"❌ 串口读取错误: {e}")
                break

            time.sleep(0.01)  # 10ms 轮询间隔

    def reconnect_serial(self):
        """重新连接串口"""
        try:
            if self.serial_port:
                self.serial_port.close()
            time.sleep(1)  # 等待1秒后重连
            self.connect_serial()
        except Exception as e:
            print(f"❌ 重连失败: {e}")
    
    def select_input_method(self):
        """选择输入方法"""
        print("\n🎯 可用的按键输入方法:")
        methods = ["keyboard"]

        if PYNPUT_AVAILABLE:
            methods.append("pynput")
        if WIN32_AVAILABLE:
            methods.append("win32")

        for i, method in enumerate(methods, 1):
            status = ""
            if method == "keyboard":
                status = " (默认)"
            elif method == "pynput":
                status = " (推荐用于游戏)"
            elif method == "win32":
                status = " (底层 API，兼容性最好)"
            print(f"  {i}. {method}{status}")

        try:
            choice = input(f"\n请选择输入方法 (1-{len(methods)}, 直接回车使用默认): ").strip()
            if choice and choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(methods):
                    self.input_method = methods[index]
                    print(f"✅ 已选择输入方法: {self.input_method}")
                else:
                    print("⚠️  无效选择，使用默认方法: keyboard")
            else:
                print("✅ 使用默认输入方法: keyboard")
        except Exception:
            print("⚠️  输入错误，使用默认方法: keyboard")

    def start(self):
        """启动控制器"""
        print("=" * 50)
        print("🎮 JoystickShield PC 控制器")
        print("=" * 50)

        # 显示可用的输入库
        print("\n📚 输入库状态:")
        print(f"  keyboard: ✅ 可用")
        print(f"  pynput: {'✅ 可用' if PYNPUT_AVAILABLE else '❌ 不可用'}")
        print(f"  win32api: {'✅ 可用' if WIN32_AVAILABLE else '❌ 不可用'}")

        # 选择输入方法
        self.select_input_method()

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

        print(f"\n🎮 当前输入方法: {self.input_method}")
        print("⌨️  按 Ctrl+C 退出")
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

        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                print("✅ 串口已关闭")
            except Exception as e:
                print(f"⚠️  关闭串口时出错: {e}")

        print("✅ 控制器已停止")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，确保资源清理"""
        self.stop()
        if exc_type:
            print(f"❌ 程序异常退出: {exc_val}")
        return False  # 不抑制异常

def check_admin_privileges():
    """检查是否有管理员权限（Windows）"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except (ImportError, AttributeError, OSError):
        return False

def main():
    # 检查基本依赖
    try:
        import importlib.util

        # 检查 pyserial
        if importlib.util.find_spec("serial") is None:
            raise ImportError("pyserial not found")

        # 检查 keyboard
        if importlib.util.find_spec("keyboard") is None:
            raise ImportError("keyboard not found")

    except ImportError:
        print("❌ 缺少基本依赖库，请安装:")
        print("pip install pyserial keyboard")
        sys.exit(1)

    # 检查可选依赖
    missing_optional = []
    if not PYNPUT_AVAILABLE:
        missing_optional.append("pynput")
    if not WIN32_AVAILABLE:
        missing_optional.append("pywin32")

    if missing_optional:
        print("⚠️  可选依赖库未安装（可提高游戏兼容性）:")
        print(f"pip install {' '.join(missing_optional)}")
        print("按 Enter 继续使用基本功能...")
        input()

    # 检查权限（Windows）
    if sys.platform.startswith('win') and not check_admin_privileges():
        print("⚠️  警告: 在 Windows 上，keyboard 库可能需要管理员权限才能正常工作")
        print("   如果遇到按键无法模拟的问题，请以管理员身份运行此程序")

    
    # 创建并启动控制器（使用上下文管理器确保资源清理）
    with JoystickController() as controller:
        controller.start()

if __name__ == "__main__":
    main()
