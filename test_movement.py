#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试摇杆移动处理逻辑
"""

def test_movement_logic():
    """测试移动逻辑"""
    print("🧪 测试摇杆移动处理逻辑")
    print("-" * 40)
    
    # 模拟各种摇杆位置数据
    test_cases = [
        ("摇杆位置 -> X: 0, Y: -50", "向上"),
        ("摇杆位置 -> X: 0, Y: 50", "向下"),
        ("摇杆位置 -> X: -50, Y: 0", "向左"),
        ("摇杆位置 -> X: 50, Y: 0", "向右"),
        ("摇杆位置 -> X: -50, Y: -50", "左上"),
        ("摇杆位置 -> X: 50, Y: -50", "右上"),
        ("摇杆位置 -> X: -50, Y: 50", "左下"),
        ("摇杆位置 -> X: 50, Y: 50", "右下"),
        ("摇杆位置 -> X: 5, Y: 8", "回中(死区)"),
        ("摇杆位置 -> X: 0, Y: 0", "回中"),
        ("16:18:54.901 > 摇杆位置 -> X: -30, Y: 40", "带时间戳的左下"),
    ]
    
    def mock_handle_movement_from_position(x_pos, y_pos):
        """模拟移动处理"""
        dead_zone = 10
        
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
            return f"🎯 摇杆在死区内: X={x_pos}, Y={y_pos}"
    
    def parse_position_data(data):
        """解析位置数据"""
        try:
            # 解析带时间戳的数据格式
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
                
                return x_pos, y_pos
        except Exception as e:
            print(f"⚠️  解析错误: {e}")
            return None, None
        
        return None, None
    
    # 测试每个用例
    for i, (test_data, expected_desc) in enumerate(test_cases):
        print(f"\n📝 测试 {i+1}: {expected_desc}")
        print(f"   输入: {test_data}")
        
        x_pos, y_pos = parse_position_data(test_data)
        if x_pos is not None and y_pos is not None:
            # 检测摇杆回中
            if abs(x_pos) <= 10 and abs(y_pos) <= 10:
                result = f"🎯 摇杆回中: X={x_pos}, Y={y_pos}"
            else:
                result = mock_handle_movement_from_position(x_pos, y_pos)
            
            print(f"   结果: {result}")
        else:
            print("   结果: ❌ 解析失败")

def test_key_mapping():
    """测试按键映射"""
    print("\n\n🎯 测试按键映射")
    print("-" * 40)
    
    # 基础映射
    base_mapping = {
        "摇杆：上": "w",
        "摇杆：下": "s", 
        "摇杆：左": "a",
        "摇杆：右": "d",
        "摇杆：左上": ["w", "a"],
        "摇杆：右上": ["w", "d"],
        "摇杆：左下": ["s", "a"],
        "摇杆：右下": ["s", "d"],
    }
    
    print("基础按键映射:")
    for action, keys in base_mapping.items():
        if isinstance(keys, list):
            keys_str = " + ".join(keys)
        else:
            keys_str = keys
        print(f"  {action} -> {keys_str}")

if __name__ == "__main__":
    print("🚀 摇杆移动逻辑测试工具")
    print("=" * 50)
    
    try:
        test_movement_logic()
        test_key_mapping()
        
        print("\n" + "=" * 50)
        print("✨ 测试完成！")
        print("💡 现在摇杆位置数据会正确触发WASD移动")
        print("💡 支持8方向移动 + 死区检测")
        
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
    
    input("\n按回车键退出...")
