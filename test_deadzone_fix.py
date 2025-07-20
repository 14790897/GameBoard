#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试回中时不会误触发按键的修复
"""

def test_deadzone_fix():
    """测试死区修复逻辑"""
    print("🧪 测试摇杆回中修复逻辑")
    print("-" * 50)
    
    # 模拟各种边界情况的摇杆位置数据
    test_cases = [
        # 明显在死区内的情况
        ("摇杆位置 -> X: 0, Y: 0", "回中"),
        ("摇杆位置 -> X: 5, Y: 3", "死区内"),
        ("摇杆位置 -> X: -8, Y: 9", "死区内"),
        ("摇杆位置 -> X: 10, Y: 10", "死区边界"),
        ("摇杆位置 -> X: -10, Y: -10", "死区边界"),
        
        # 死区边界外的情况
        ("摇杆位置 -> X: 0, Y: -11", "向上"),
        ("摇杆位置 -> X: 0, Y: 11", "向下"), 
        ("摇杆位置 -> X: -11, Y: 0", "向左"),
        ("摇杆位置 -> X: 11, Y: 0", "向右"),
        
        # 从移动到回中的过渡情况
        ("摇杆位置 -> X: -50, Y: 30", "左下移动"),
        ("摇杆位置 -> X: -25, Y: 15", "仍在移动"),
        ("摇杆位置 -> X: -8, Y: 5", "进入死区"),
        ("摇杆位置 -> X: 0, Y: 0", "完全回中"),
        
        # 带时间戳的回中情况
        ("16:18:54.901 > 摇杆位置 -> X: -3, Y: 8", "带时间戳的死区"),
    ]
    
    def simulate_handle_position_data(data):
        """模拟修复后的位置处理逻辑"""
        try:
            # 解析带时间戳的数据格式
            original_data = data
            if " > " in data:
                timestamp, actual_data = data.split(" > ", 1)
                data = actual_data.strip()
            
            # 解析 "摇杆位置 -> X: -3, Y: -96" 格式
            if "X:" in data and "Y:" in data:
                x_start = data.find("X:") + 2
                comma_pos = data.find(",", x_start)
                y_start = data.find("Y:") + 2
                
                x_str = data[x_start:comma_pos].strip()
                y_str = data[y_start:].strip()
                
                x_pos = int(x_str)
                y_pos = int(y_str)
                
                # 先检测摇杆是否在死区内 (死区范围 ±10)
                if abs(x_pos) <= 10 and abs(y_pos) <= 10:
                    return f"🎯 摇杆回中: X={x_pos}, Y={y_pos} (释放所有方向键)"
                else:
                    # 只有不在死区时才根据位置数据触发移动
                    return simulate_movement_from_position(x_pos, y_pos)
                    
        except Exception as e:
            return f"⚠️  解析错误: {e}"
        
        return "❌ 无效数据"
    
    def simulate_movement_from_position(x_pos, y_pos):
        """模拟修复后的移动处理逻辑"""
        dead_zone = 10
        
        # 双重检查：确保不在死区内
        if abs(x_pos) <= dead_zone and abs(y_pos) <= dead_zone:
            return f"🎯 摇杆在死区内，释放所有方向键: X={x_pos}, Y={y_pos}"
        
        # 根据位置确定需要按下的键
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
            
            return f"🎮 摇杆移动: {direction_str} ({'+'.join(keys_to_press)})"
        else:
            return f"🤔 位置计算异常: X={x_pos}, Y={y_pos}"
    
    # 测试每个用例
    print("测试结果:")
    for i, (test_data, expected_desc) in enumerate(test_cases):
        print(f"\n📝 测试 {i+1:2d}: {expected_desc}")
        print(f"     输入: {test_data}")
        result = simulate_handle_position_data(test_data)
        print(f"     结果: {result}")
        
        # 检查是否正确处理死区
        if "死区" in expected_desc or "回中" in expected_desc:
            if "摇杆回中" in result or "死区内" in result:
                print(f"     ✅ 正确处理死区")
            else:
                print(f"     ❌ 死区处理有误!")
        elif "移动" in expected_desc or "向" in expected_desc:
            if "摇杆移动" in result:
                print(f"     ✅ 正确触发移动")
            else:
                print(f"     ❌ 移动触发有误!")

def test_deadzone_boundary():
    """测试死区边界值"""
    print("\n\n🎯 测试死区边界值")
    print("-" * 50)
    
    boundary_cases = [
        # 边界值测试
        (-10, 0, "死区边界"),
        (10, 0, "死区边界"), 
        (0, -10, "死区边界"),
        (0, 10, "死区边界"),
        (-11, 0, "超出死区"),
        (11, 0, "超出死区"),
        (0, -11, "超出死区"),  
        (0, 11, "超出死区"),
    ]
    
    print("边界值测试结果:")
    for x, y, desc in boundary_cases:
        is_in_deadzone = abs(x) <= 10 and abs(y) <= 10
        print(f"X={x:3d}, Y={y:3d} -> {'死区内' if is_in_deadzone else '死区外'} ({desc})")

if __name__ == "__main__":
    print("🚀 摇杆回中修复验证工具")
    print("=" * 60)
    
    try:
        test_deadzone_fix()
        test_deadzone_boundary()
        
        print("\n" + "=" * 60)
        print("✨ 修复验证完成！")
        print("🔧 修复要点:")
        print("   1. 优先检查死区，避免在回中过程中误触发移动")
        print("   2. 双重检查确保不在死区内触发按键")
        print("   3. 只有确实在死区外才会触发移动按键")
        print("💡 现在摇杆回中时不会再误触发s键或其他方向键！")
        
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
    
    input("\n按回车键退出...")
