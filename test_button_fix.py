#!/usr/bin/env python3
"""
按键功能测试脚本
直接测试修复后的按键处理逻辑
"""

import time
from collections import defaultdict
import keyboard

class ButtonTestSimulator:
    def __init__(self):
        # 按键映射配置（复制自 joystick_controller.py）
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
            "上按钮按下": "up",      # 修复：改为方向键上
            "下按钮按下": "down",    # 修复：改为方向键下
            "左按钮按下": "left",    # 修复：改为方向键左
            "右按钮按下": "right",   # 保持方向键右
            "E 按钮按下": "e",
            "F 按钮按下": "f",
            
            # 特殊功能
            "摇杆偏离中心": None,  # 不映射按键
        }
        
        self.key_states = defaultdict(bool)  # 记录按键状态
        self.button_states = defaultdict(bool)  # 记录按钮状态
        self.last_button_time = defaultdict(float)  # 记录按钮最后触发时间
        self.button_debounce_time = 0.1  # 按钮防抖时间（100ms）
        
    def press_keys_continuous(self, keys):
        """按下按键（针对摇杆方向，持续状态）"""
        if isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            if not self.key_states[key]:
                print(f"🔽 摇杆持续按下: {key}")
                self.key_states[key] = True
    
    def press_keys(self, keys):
        """按下按键（针对按钮事件，执行按下-释放）"""
        if isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            # 对于按钮事件，执行完整的按下-释放动作
            print(f"🔽 按钮瞬时按下: {key}")
            time.sleep(0.05)  # 短暂延迟确保按键被识别
            print(f"🔼 按钮瞬时释放: {key}")
    
    def should_process_button_event(self, button_data):
        """判断是否应该处理按钮事件（防抖）"""
        current_time = time.time()
        last_time = self.last_button_time.get(button_data, 0)
        
        # 如果距离上次触发的时间超过防抖时间，则允许处理
        return current_time - last_time > self.button_debounce_time
    
    def handle_data(self, data):
        """处理数据（模拟主程序逻辑）"""
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
                    print(f"❌ 无映射: {data}")
            else:
                print(f"🚫 按钮防抖: {data} (忽略重复触发)")
        else:
            # 摇杆方向事件 - 持续按压处理
            if data in self.key_mapping:
                keys = self.key_mapping[data]
                if keys:
                    self.press_keys_continuous(keys)  # 摇杆方向用持续按压
            else:
                print(f"❌ 无映射: {data}")
    
    def test_button_events(self):
        """测试按钮事件"""
        print("🧪 开始测试按钮事件...")
        print("=" * 50)
        
        test_events = [
            "上按钮按下",
            "下按钮按下", 
            "左按钮按下",
            "右按钮按下",
            "摇杆按键按下",
            "E 按钮按下",
            "F 按钮按下"
        ]
        
        for i, event in enumerate(test_events):
            print(f"\n🧪 测试 {i+1}: {event}")
            self.handle_data(event)
            time.sleep(0.2)  # 等待防抖时间
            
        print("\n" + "=" * 50)
        print("✅ 按钮事件测试完成!")
        
        # 测试重复事件（应该被防抖阻止）
        print("\n🧪 测试防抖机制...")
        print("=" * 30)
        
        print("\n🔄 快速重复按下 '上按钮按下' (应该被防抖)")
        self.handle_data("上按钮按下")
        time.sleep(0.05)  # 短于防抖时间
        self.handle_data("上按钮按下")  # 应该被阻止
        
        time.sleep(0.2)  # 等待防抖时间过去
        print("\n🔄 等待防抖时间后再次按下 (应该成功)")
        self.handle_data("上按钮按下")  # 应该成功

if __name__ == "__main__":
    try:
        print("⚠️  注意: 这是模拟测试，不会实际按键")
        tester = ButtonTestSimulator()
        tester.test_button_events()
    except KeyboardInterrupt:
        print("\n👋 测试中断")
    except Exception as e:
        print(f"❌ 测试异常: {e}")
