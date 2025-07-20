#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摇杆回中行为实时监控工具
直接读取 joystick_controller.py 的逻辑来测试
"""

import time
from collections import defaultdict

class JoystickMonitor:
    def __init__(self):
        self.key_states = defaultdict(bool)
        self.last_position = {"x": 0, "y": 0}
        self.position_history = []
        self.max_history = 3
        
    def update_position_history(self, x_pos, y_pos):
        """更新位置历史记录"""
        self.position_history.append({"x": x_pos, "y": y_pos})
        
        # 保持历史记录数量不超过最大值
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)
    
    def is_returning_to_center(self, x_pos, y_pos):
        """判断摇杆是否正在回中"""
        if len(self.position_history) < 2:
            return False
        
        # 计算当前位置到中心的距离
        current_distance = abs(x_pos) + abs(y_pos)
        
        # 计算前一个位置到中心的距离
        prev_pos = self.position_history[-2]
        prev_distance = abs(prev_pos["x"]) + abs(prev_pos["y"])
        
        # 如果距离在减小，说明正在向中心移动
        is_approaching_center = current_distance < prev_distance
        
        # 如果前一个位置不在死区内，而且正在向中心靠近，认为是回中过程
        dead_zone = 10
        prev_in_deadzone = abs(prev_pos["x"]) <= dead_zone and abs(prev_pos["y"]) <= dead_zone
        
        # 回中判断条件：
        # 1. 正在向中心靠近
        # 2. 前一个位置不在死区内（避免在死区内的小幅震动）
        # 3. 当前位置距离中心的距离小于前一个位置的80%（明显的回中趋势）
        return (is_approaching_center and 
                not prev_in_deadzone and 
                current_distance < prev_distance * 0.8)
    
    def simulate_position_processing(self, x_pos, y_pos):
        """模拟位置处理"""
        # 更新位置历史
        self.update_position_history(x_pos, y_pos)
        
        result = {
            "position": (x_pos, y_pos),
            "in_deadzone": False,
            "returning": False,
            "action": "",
            "keys_pressed": [],
            "keys_released": []
        }
        
        # 先检测摇杆是否在死区内 (死区范围 ±10)
        if abs(x_pos) <= 10 and abs(y_pos) <= 10:
            result["in_deadzone"] = True
            result["action"] = "回中"
            # 模拟释放所有方向键
            direction_keys = ["w", "a", "s", "d"]
            for key in direction_keys:
                if self.key_states[key]:
                    result["keys_released"].append(key)
                    self.key_states[key] = False
        else:
            # 检查是否正在回中过程中
            if self.is_returning_to_center(x_pos, y_pos):
                result["returning"] = True
                result["action"] = "正在回中，跳过移动"
                return result
            
            # 模拟移动处理
            result["action"] = "移动"
            
            # 先释放所有方向键
            direction_keys = ["w", "a", "s", "d"]
            for key in direction_keys:
                if self.key_states[key]:
                    result["keys_released"].append(key)
                    self.key_states[key] = False
            
            # 根据位置确定需要按下的键
            dead_zone = 10
            
            # 垂直方向 (Y轴)
            if y_pos < -dead_zone:  # 向上
                result["keys_pressed"].append("w")
                self.key_states["w"] = True
            elif y_pos > dead_zone:  # 向下
                result["keys_pressed"].append("s")
                self.key_states["s"] = True
                
            # 水平方向 (X轴)
            if x_pos < -dead_zone:  # 向左
                result["keys_pressed"].append("a")
                self.key_states["a"] = True
            elif x_pos > dead_zone:  # 向右
                result["keys_pressed"].append("d")
                self.key_states["d"] = True
        
        # 更新最后位置
        self.last_position = {"x": x_pos, "y": y_pos}
        
        return result

def test_joystick_scenarios():
    """测试各种摇杆场景"""
    print("🎮 摇杆回中行为实时监控测试")
    print("=" * 70)
    
    monitor = JoystickMonitor()
    
    # 测试场景1：从上方回中
    print("\n📝 场景1: 摇杆从上方回中")
    print("-" * 50)
    
    up_to_center = [
        (0, -80),   # 向上推到底
        (0, -60),   # 开始回来
        (0, -40),   # 继续回中
        (0, -20),   # 接近中心
        (0, -8),    # 进入死区
        (0, 0),     # 完全回中
    ]
    
    for i, (x, y) in enumerate(up_to_center):
        result = monitor.simulate_position_processing(x, y)
        
        print(f"步骤 {i+1}: X={x:3d}, Y={y:3d}")
        print(f"       状态: {result['action']}")
        print(f"       死区: {'是' if result['in_deadzone'] else '否'}")
        print(f"       回中: {'是' if result['returning'] else '否'}")
        
        if result['keys_pressed']:
            print(f"       按下: {', '.join(result['keys_pressed'])}")
        if result['keys_released']:
            print(f"       释放: {', '.join(result['keys_released'])}")
        
        # 检查是否有问题
        if result['keys_pressed'] and 's' in result['keys_pressed'] and y <= 0:
            print(f"       ❌ 警告: 摇杆向上但触发了's'键!")
        elif not result['keys_pressed'] and not result['in_deadzone'] and not result['returning']:
            print(f"       ⚠️  注意: 应该触发移动但没有按键")
        else:
            print(f"       ✅ 行为正常")
        
        print()
    
    # 重置监控器
    monitor = JoystickMonitor()
    
    # 测试场景2：快速上下摆动
    print("\n📝 场景2: 摇杆快速上下摆动")
    print("-" * 50)
    
    oscillation = [
        (0, -30),   # 向上
        (0, -15),   # 回中一点
        (0, -35),   # 又向上
        (0, -10),   # 回中
        (0, 0),     # 中心
        (0, 15),    # 向下一点
        (0, 5),     # 回中
        (0, 0),     # 完全回中
    ]
    
    for i, (x, y) in enumerate(oscillation):
        result = monitor.simulate_position_processing(x, y)
        
        print(f"步骤 {i+1}: X={x:3d}, Y={y:3d} -> {result['action']}")
        
        if result['keys_pressed']:
            print(f"       按下: {', '.join(result['keys_pressed'])}")
        if result['keys_released']:
            print(f"       释放: {', '.join(result['keys_released'])}")
            
        # 检查按键冲突
        pressed_keys = set(result['keys_pressed'])
        if 'w' in pressed_keys and 's' in pressed_keys:
            print(f"       ❌ 错误: 同时按下w和s!")
        elif 'a' in pressed_keys and 'd' in pressed_keys:
            print(f"       ❌ 错误: 同时按下a和d!")
        else:
            print(f"       ✅ 无按键冲突")
        print()

def display_key_states_summary():
    """显示按键状态总结"""
    print("\n💡 修复要点总结:")
    print("=" * 50)
    print("1. 添加了位置历史记录，跟踪摇杆移动趋势")
    print("2. 检测回中过程，避免在回中时触发相反方向")
    print("3. 只有明确的方向移动才会触发按键")
    print("4. 死区检测确保小幅震动不会触发按键")
    print("\n🎯 预期效果:")
    print("- 摇杆向上推再回来：只触发w键，不会误触发s键")
    print("- 摇杆在死区内：不触发任何方向键")
    print("- 明确的方向移动：正常触发对应方向键")

if __name__ == "__main__":
    try:
        test_joystick_scenarios()
        display_key_states_summary()
        
        print("\n" + "=" * 70)
        print("✨ 监控测试完成！")
        print("💡 现在可以运行实际的控制器来验证修复效果")
        
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
    
    input("\n按回车键退出...")
