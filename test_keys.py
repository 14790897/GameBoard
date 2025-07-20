#!/usr/bin/env python3
"""
按键测试工具
用于测试不同的按键模拟方法是否能被游戏识别
"""

import time
import sys

# 尝试导入各种输入库
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

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

class KeyTester:
    def __init__(self):
        self.pynput_controller = None
        if PYNPUT_AVAILABLE:
            try:
                self.pynput_controller = pynput_kb.Controller()
            except Exception as e:
                print(f"pynput 初始化失败: {e}")
        
        # Windows 虚拟键码映射
        self.vk_codes = {
            'w': 0x57, 'a': 0x41, 's': 0x53, 'd': 0x44,
            'space': 0x20, 'e': 0x45, 'f': 0x46,
            'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27
        }
    
    def test_keyboard_lib(self, key):
        """测试 keyboard 库"""
        if not KEYBOARD_AVAILABLE:
            return False
        try:
            print(f"  使用 keyboard 库测试 {key}...")
            keyboard.press(key)
            time.sleep(0.1)
            keyboard.release(key)
            return True
        except Exception as e:
            print(f"  ❌ keyboard 库失败: {e}")
            return False
    
    def test_pynput_lib(self, key):
        """测试 pynput 库"""
        if not self.pynput_controller:
            return False
        try:
            print(f"  使用 pynput 库测试 {key}...")
            if key in ['up', 'down', 'left', 'right']:
                key_map = {
                    'up': pynput_kb.Key.up,
                    'down': pynput_kb.Key.down,
                    'left': pynput_kb.Key.left,
                    'right': pynput_kb.Key.right
                }
                self.pynput_controller.press(key_map[key])
                time.sleep(0.1)
                self.pynput_controller.release(key_map[key])
            elif key == 'space':
                self.pynput_controller.press(pynput_kb.Key.space)
                time.sleep(0.1)
                self.pynput_controller.release(pynput_kb.Key.space)
            else:
                self.pynput_controller.press(key)
                time.sleep(0.1)
                self.pynput_controller.release(key)
            return True
        except Exception as e:
            print(f"  ❌ pynput 库失败: {e}")
            return False
    
    def test_win32_api(self, key):
        """测试 Win32 API"""
        if not WIN32_AVAILABLE or key not in self.vk_codes:
            return False
        try:
            print(f"  使用 Win32 API 测试 {key}...")
            vk_code = self.vk_codes[key]
            win32api.keybd_event(vk_code, 0, 0, 0)  # 按下
            time.sleep(0.1)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放
            return True
        except Exception as e:
            print(f"  ❌ Win32 API 失败: {e}")
            return False
    
    def test_key(self, key):
        """测试单个按键的所有方法"""
        print(f"\n🔍 测试按键: {key}")
        print("请在游戏中观察是否有响应...")
        
        success_count = 0
        
        if self.test_keyboard_lib(key):
            success_count += 1
        
        time.sleep(1)  # 间隔1秒
        
        if self.test_pynput_lib(key):
            success_count += 1
        
        time.sleep(1)  # 间隔1秒
        
        if self.test_win32_api(key):
            success_count += 1
        
        print(f"  ✅ {success_count}/3 种方法成功")
        return success_count > 0
    
    def run_test(self):
        """运行完整测试"""
        print("=" * 50)
        print("🧪 按键测试工具")
        print("=" * 50)
        
        print("\n📚 可用库状态:")
        print(f"  keyboard: {'✅' if KEYBOARD_AVAILABLE else '❌'}")
        print(f"  pynput: {'✅' if PYNPUT_AVAILABLE else '❌'}")
        print(f"  win32api: {'✅' if WIN32_AVAILABLE else '❌'}")
        
        print("\n⚠️  请先打开游戏或文本编辑器来观察按键效果")
        print("测试将在 5 秒后开始...")
        
        for i in range(5, 0, -1):
            print(f"倒计时: {i}")
            time.sleep(1)
        
        # 测试常用按键
        test_keys = ['w', 'a', 's', 'd', 'space', 'e']
        
        for key in test_keys:
            self.test_key(key)
            time.sleep(2)  # 每个按键测试间隔2秒
        
        print("\n" + "=" * 50)
        print("🎯 测试完成！")
        print("如果某些方法在游戏中有效，请在 joystick_controller.py 中")
        print("选择相应的输入方法。")
        print("=" * 50)

def main():
    tester = KeyTester()
    tester.run_test()

if __name__ == "__main__":
    main()
