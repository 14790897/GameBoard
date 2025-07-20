#!/usr/bin/env python3
"""
摇杆抖动修复测试脚本
模拟摇杆数据，测试新的防抖逻辑
"""

import time
from collections import defaultdict

class JoystickStabilityTest:
    def __init__(self):
        self.key_states = defaultdict(bool)
        
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
        """新的移动处理逻辑（复制自修复后的代码）"""
        # 死区范围 - 增加死区以减少抖动
        dead_zone = 20  # 从10增加到20
        
        # 滞后区域 - 避免在阈值边界处抖动
        hysteresis = 5  # 滞后范围
        
        print(f"📍 处理位置: X={x_pos}, Y={y_pos}")
        
        # 双重检查：确保不在死区内
        if abs(x_pos) <= dead_zone and abs(y_pos) <= dead_zone:
            # 如果在死区内，释放所有方向键
            direction_keys = ["w", "a", "s", "d"]
            keys_to_release = [key for key in direction_keys if self.key_states[key]]
            
            if keys_to_release:
                for key in keys_to_release:
                    self.release_keys(key)
                print(f"🎯 摇杆在死区内，释放所有方向键: X={x_pos}, Y={y_pos}")
            return
        
        # 根据位置确定需要按下的键，使用滞后处理
        keys_to_press = []
        
        # 垂直方向 (Y轴) - 添加滞后处理
        current_y_pressed = self.key_states["w"] or self.key_states["s"]
        if not current_y_pressed:
            # 没有Y轴按键被按下，使用标准阈值
            if y_pos < -(dead_zone):  # 向上
                keys_to_press.append("w")
            elif y_pos > dead_zone:  # 向下
                keys_to_press.append("s")
        else:
            # 有Y轴按键被按下，使用滞后阈值避免抖动
            if y_pos < -(dead_zone - hysteresis):  # 向上（滞后）
                keys_to_press.append("w")
            elif y_pos > (dead_zone - hysteresis):  # 向下（滞后）
                keys_to_press.append("s")
            
        # 水平方向 (X轴) - 添加滞后处理
        current_x_pressed = self.key_states["a"] or self.key_states["d"]
        if not current_x_pressed:
            # 没有X轴按键被按下，使用标准阈值
            if x_pos < -(dead_zone):  # 向左
                keys_to_press.append("a")
            elif x_pos > dead_zone:  # 向右
                keys_to_press.append("d")
        else:
            # 有X轴按键被按下，使用滞后阈值避免抖动
            if x_pos < -(dead_zone - hysteresis):  # 向左（滞后）
                keys_to_press.append("a")
            elif x_pos > (dead_zone - hysteresis):  # 向右（滞后）
                keys_to_press.append("d")
        
        # 智能按键管理：只改变有差异的按键状态
        direction_keys = ["w", "a", "s", "d"]
        keys_to_press_set = set(keys_to_press)
        currently_pressed_set = set(key for key in direction_keys if self.key_states[key])
        
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
    
    def test_joystick_stability(self):
        """测试摇杆稳定性"""
        print("🧪 测试摇杆抖动修复...")
        print("=" * 50)
        
        # 测试场景1：摇杆向上移动，但有轻微抖动
        print("\n📋 场景1：向上移动但有轻微Y轴抖动")
        test_positions = [
            (0, -25),    # 明确向上
            (0, -22),    # 轻微向上抖动
            (0, -24),    # 再次向上
            (0, -21),    # 再次轻微抖动
            (0, -23),    # 向上
            (0, -25),    # 向上
        ]
        
        for i, (x, y) in enumerate(test_positions):
            print(f"\n步骤 {i+1}:")
            self.handle_movement_from_position(x, y)
            time.sleep(0.1)
        
        # 测试场景2：从向上移动到回中
        print("\n📋 场景2：从向上移动到回中")
        test_positions_2 = [
            (0, -25),    # 向上
            (0, -18),    # 向中心靠近
            (0, -15),    # 接近死区
            (0, -10),    # 进入死区
            (0, 5),      # 中心
        ]
        
        for i, (x, y) in enumerate(test_positions_2):
            print(f"\n步骤 {i+1}:")
            self.handle_movement_from_position(x, y)
            time.sleep(0.1)
            
        # 测试场景3：在阈值边界附近抖动
        print("\n📋 场景3：阈值边界抖动测试")
        test_positions_3 = [
            (0, -21),    # 刚好超过阈值
            (0, -19),    # 刚好低于阈值
            (0, -20),    # 在阈值上
            (0, -18),    # 低于阈值
            (0, -22),    # 超过阈值
        ]
        
        for i, (x, y) in enumerate(test_positions_3):
            print(f"\n步骤 {i+1}:")
            self.handle_movement_from_position(x, y)
            time.sleep(0.1)
            
        print("\n" + "=" * 50)
        print("🎯 测试完成!")
        print(f"当前按键状态: {dict(self.key_states)}")

if __name__ == "__main__":
    tester = JoystickStabilityTest()
    tester.test_joystick_stability()
