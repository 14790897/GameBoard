#!/usr/bin/env python3
"""
新按键映射测试脚本
测试 ijhl 方向键映射是否正确工作
"""

import time
from collections import defaultdict

class NewKeyMappingTest:
    def __init__(self):
        self.key_states = defaultdict(bool)
        
        # 新的按键映射配置
        self.key_mapping = {
            # 摇杆方向 -> 键盘按键 (与按钮映射保持一致)
            "摇杆：上": "i",      # 对应上按钮
            "摇杆：下": "j",      # 对应下按钮
            "摇杆：左": "h",      # 对应左按钮
            "摇杆：右": "l",      # 对应右按钮
            "摇杆：左上": ["i", "h"],    # 上+左
            "摇杆：右上": ["i", "l"],    # 上+右
            "摇杆：左下": ["j", "h"],    # 下+左
            "摇杆：右下": ["j", "l"],    # 下+右
            
            # 按钮 -> 键盘按键
            "摇杆按键按下": "space",
            "上按钮按下": "i",
            "下按钮按下": "j",
            "左按钮按下": "h",
            "右按钮按下": "l",
            "E 按钮按下": "e",
            "F 按钮按下": "f",
        }
        
    def press_keys_continuous(self, keys):
        """模拟持续按键"""
        if isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            if not self.key_states[key]:
                print(f"🔽 按下: {key}")
                self.key_states[key] = True
    
    def release_keys(self, keys):
        """模拟释放按键"""
        if isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            if self.key_states[key]:
                print(f"🔼 释放: {key}")
                self.key_states[key] = False
    
    def handle_movement_from_position(self, x_pos, y_pos):
        """新的移动处理逻辑（使用ijhl键位）"""
        # 死区范围
        dead_zone = 20
        hysteresis = 5
        
        print(f"📍 处理位置: X={x_pos}, Y={y_pos}")
        
        # 双重检查：确保不在死区内
        if abs(x_pos) <= dead_zone and abs(y_pos) <= dead_zone:
            # 如果在死区内，释放所有方向键
            direction_keys = ["i", "h", "j", "l"]  # 新的方向键
            keys_to_release = [key for key in direction_keys if self.key_states[key]]
            
            if keys_to_release:
                for key in keys_to_release:
                    self.release_keys(key)
                print(f"🎯 摇杆在死区内，释放所有方向键: X={x_pos}, Y={y_pos}")
            return
        
        # 根据位置确定需要按下的键
        keys_to_press = []
        
        # 垂直方向 (Y轴) - 使用 i(上) 和 j(下)
        current_y_pressed = self.key_states["i"] or self.key_states["j"]
        if not current_y_pressed:
            if y_pos < -(dead_zone):  # 向上
                keys_to_press.append("i")
            elif y_pos > dead_zone:  # 向下
                keys_to_press.append("j")
        else:
            if y_pos < -(dead_zone - hysteresis):  # 向上（滞后）
                keys_to_press.append("i")
            elif y_pos > (dead_zone - hysteresis):  # 向下（滞后）
                keys_to_press.append("j")
            
        # 水平方向 (X轴) - 使用 h(左) 和 l(右)
        current_x_pressed = self.key_states["h"] or self.key_states["l"]
        if not current_x_pressed:
            if x_pos < -(dead_zone):  # 向左
                keys_to_press.append("h")
            elif x_pos > dead_zone:  # 向右
                keys_to_press.append("l")
        else:
            if x_pos < -(dead_zone - hysteresis):  # 向左（滞后）
                keys_to_press.append("h")
            elif x_pos > (dead_zone - hysteresis):  # 向右（滞后）
                keys_to_press.append("l")
        
        # 智能按键管理
        direction_keys = ["i", "h", "j", "l"]  # 上左下右
        keys_to_press_set = set(keys_to_press)
        currently_pressed_set = set(key for key in direction_keys if self.key_states[key])
        
        # 需要释放的键
        keys_to_release = currently_pressed_set - keys_to_press_set
        for key in keys_to_release:
            self.release_keys(key)
            
        # 需要按下的键
        keys_to_press_new = keys_to_press_set - currently_pressed_set
        for key in keys_to_press_new:
            self.press_keys_continuous([key])
        
        # 只在有按键变化时输出日志
        if keys_to_release or keys_to_press_new:
            if keys_to_press:
                direction_str = ""
                if "i" in keys_to_press and "h" in keys_to_press:
                    direction_str = "左上"
                elif "i" in keys_to_press and "l" in keys_to_press:
                    direction_str = "右上"
                elif "j" in keys_to_press and "h" in keys_to_press:
                    direction_str = "左下"
                elif "j" in keys_to_press and "l" in keys_to_press:
                    direction_str = "右下"
                elif "i" in keys_to_press:
                    direction_str = "上"
                elif "j" in keys_to_press:
                    direction_str = "下"
                elif "h" in keys_to_press:
                    direction_str = "左"
                elif "l" in keys_to_press:
                    direction_str = "右"
                
                print(f"🎮 摇杆移动: {direction_str} ({'+'.join(keys_to_press)})")
            else:
                print("🎯 摇杆回中，释放所有方向键")
    
    def test_new_mapping(self):
        """测试新的 ijhl 按键映射"""
        print("🧪 测试新的 ijhl 按键映射...")
        print("=" * 50)
        
        # 测试各个方向
        test_positions = [
            (0, -30, "上方向 -> i 键"),
            (0, 30, "下方向 -> j 键"),
            (-30, 0, "左方向 -> h 键"),
            (30, 0, "右方向 -> l 键"),
            (-30, -30, "左上方向 -> h+i 键"),
            (30, -30, "右上方向 -> l+i 键"),
            (-30, 30, "左下方向 -> h+j 键"),
            (30, 30, "右下方向 -> l+j 键"),
            (0, 0, "回中 -> 释放所有键"),
        ]
        
        for i, (x, y, description) in enumerate(test_positions):
            print(f"\n📋 测试 {i+1}: {description}")
            self.handle_movement_from_position(x, y)
            time.sleep(0.2)
            
        print("\n" + "=" * 50)
        print("🎯 测试完成!")
        print(f"最终按键状态: {dict(self.key_states)}")
        
        # 验证按键映射
        print("\n📋 按键映射确认:")
        direction_mappings = {
            "上": "i", "下": "j", "左": "h", "右": "l"
        }
        for direction, key in direction_mappings.items():
            print(f"  摇杆{direction} -> {key} 键")
    
    def test_button_mapping(self):
        """测试按钮映射"""
        print("\n🧪 测试按钮映射...")
        print("=" * 30)
        
        button_events = [
            "上按钮按下",
            "下按钮按下", 
            "左按钮按下",
            "右按钮按下"
        ]
        
        for event in button_events:
            if event in self.key_mapping:
                key = self.key_mapping[event]
                print(f"✅ {event} -> {key} 键")
            else:
                print(f"❌ {event} -> 无映射")

if __name__ == "__main__":
    tester = NewKeyMappingTest()
    tester.test_new_mapping()
    tester.test_button_mapping()
