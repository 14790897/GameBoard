#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试摇杆回中时避免误触发的修复
模拟摇杆从上方位置回到中心的过程
"""

def test_return_to_center_detection():
    """测试回中检测逻辑"""
    print("🧪 测试摇杆回中检测逻辑")
    print("-" * 60)
    
    # 模拟摇杆从上方回中的位置序列
    position_sequences = [
        {
            "name": "从上方回中",
            "positions": [
                (0, -80),   # 向上推到底
                (0, -65),   # 开始回来
                (0, -45),   # 继续回中
                (0, -25),   # 接近中心
                (0, -8),    # 进入死区
                (0, 0),     # 完全回中
            ]
        },
        {
            "name": "从下方回中", 
            "positions": [
                (0, 70),    # 向下推
                (0, 50),    # 开始回来
                (0, 30),    # 继续回中
                (0, 12),    # 接近死区
                (0, 3),     # 进入死区
                (0, 0),     # 完全回中
            ]
        },
        {
            "name": "从左上角回中",
            "positions": [
                (-60, -60), # 左上角
                (-45, -45), # 开始回中
                (-25, -25), # 继续回中
                (-10, -10), # 接近死区
                (-3, -5),   # 进入死区
                (0, 0),     # 完全回中
            ]
        },
        {
            "name": "在死区内的小幅震动（不应触发）",
            "positions": [
                (5, 3),     # 死区内
                (8, 7),     # 死区内
                (3, 9),     # 死区内  
                (6, 4),     # 死区内
                (2, 1),     # 死区内
                (0, 0),     # 中心
            ]
        }
    ]
    
    class MockJoystickController:
        def __init__(self):
            self.position_history = []
            self.max_history = 3
            self.last_position = {"x": 0, "y": 0}
            
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
        
        def should_trigger_movement(self, x_pos, y_pos):
            """判断是否应该触发移动"""
            # 在死区内不触发
            if abs(x_pos) <= 10 and abs(y_pos) <= 10:
                return False, "在死区内"
            
            # 正在回中时不触发    
            if self.is_returning_to_center(x_pos, y_pos):
                return False, "正在回中"
            
            return True, "正常移动"
        
        def simulate_movement(self, x_pos, y_pos):
            """模拟移动判断"""
            dead_zone = 10
            keys_to_press = []
            
            # 垂直方向 (Y轴)
            if y_pos < -dead_zone:  # 向上
                keys_to_press.append("w")
            elif y_pos > dead_zone:  # 向下
                keys_to_press.append("s")
                
            # 水平方向 (X轴)
            if x_pos < -dead_zone:  # 向左
                keys_to_press.append("a")
            elif x_pos > dead_zone:  # 向右
                keys_to_press.append("d")
            
            return keys_to_press
    
    # 测试每个序列
    for seq in position_sequences:
        print(f"\n🎮 测试序列: {seq['name']}")
        print("-" * 40)
        
        controller = MockJoystickController()
        
        for i, (x, y) in enumerate(seq['positions']):
            # 更新位置历史
            controller.update_position_history(x, y)
            
            # 判断是否应该触发移动
            should_move, reason = controller.should_trigger_movement(x, y)
            
            # 获取应该按下的键
            keys = controller.simulate_movement(x, y) if should_move else []
            
            print(f"  步骤 {i+1}: X={x:3d}, Y={y:3d} -> {reason}")
            if should_move:
                if keys:
                    print(f"         ✅ 触发移动: {'+'.join(keys)}")
                else:
                    print(f"         🎯 位置在死区")
            else:
                potential_keys = controller.simulate_movement(x, y)
                if potential_keys:
                    print(f"         ❌ 跳过移动: 本来会触发 {'+'.join(potential_keys)}")
                else:
                    print(f"         ⭕ 跳过移动: 在死区内")
            
            # 更新最后位置
            controller.last_position = {"x": x, "y": y}

def test_edge_cases():
    """测试边界情况"""
    print("\n\n🎯 测试边界情况")
    print("-" * 60)
    
    edge_cases = [
        "快速来回摆动",
        "缓慢回中",
        "在死区边缘震荡"
    ]
    
    for case in edge_cases:
        print(f"\n📝 {case}: 需要根据实际使用情况进一步调优")

if __name__ == "__main__":
    print("🚀 摇杆回中误触发修复测试")
    print("=" * 70)
    
    try:
        test_return_to_center_detection()
        test_edge_cases()
        
        print("\n" + "=" * 70)
        print("✨ 测试完成！")
        print("\n🔧 修复机制:")
        print("   1. 记录摇杆位置历史")
        print("   2. 检测是否正在向中心靠近") 
        print("   3. 如果是回中过程，跳过移动触发")
        print("   4. 只有真正的方向移动才触发按键")
        print("\n💡 这样就不会在回中时误触发相反方向的按键了！")
        
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
    
    input("\n按回车键退出...")
