#!/usr/bin/env python3
"""
测试脚本 - 验证数据解析功能
"""

def test_data_parsing():
    """测试数据解析功能"""
    
    # 测试数据 (从你提供的串口输出)
    test_data = [
        "16:18:54.901 > 摇杆位置 -> X: -3, Y: -96",
        "16:18:54.999 > 摇杆：下", 
        "16:18:54.999 > 摇杆偏离中心",
        "16:18:55.002 > 摇杆位置 -> X: 0, Y: -28",
        "16:20:08.303 > 摇杆：上",
        "16:20:08.303 > 摇杆偏离中心",
        "16:24:25.419 > 摇杆：上"
    ]
    
    print("🧪 测试数据解析功能")
    print("=" * 50)
    
    for raw_data in test_data:
        print(f"原始数据: {raw_data}")
        
        # 解析时间戳
        if " > " in raw_data:
            timestamp, actual_data = raw_data.split(" > ", 1)
            actual_data = actual_data.strip()
            print(f"  时间戳: {timestamp}")
            print(f"  实际数据: {actual_data}")
            
            # 判断数据类型
            if "摇杆位置" in actual_data:
                print(f"  📍 类型: 位置数据")
                # 解析位置
                try:
                    if "X:" in actual_data and "Y:" in actual_data:
                        parts = actual_data.split("X:")[1].split(",")
                        x_str = parts[0].strip()
                        y_str = parts[1].split("Y:")[1].strip()
                        x_pos = int(x_str)
                        y_pos = int(y_str)
                        print(f"    解析结果: X={x_pos}, Y={y_pos}")
                        
                        # 判断是否回中
                        if abs(x_pos) <= 10 and abs(y_pos) <= 10:
                            print(f"    🎯 摇杆回中!")
                        else:
                            print(f"    📍 摇杆偏移")
                except Exception as e:
                    print(f"    ❌ 解析错误: {e}")
                    
            elif "摇杆：" in actual_data:
                print(f"  🕹️ 类型: 方向事件")
                direction = actual_data.replace("摇杆：", "")
                print(f"    方向: {direction}")
                
            elif "按钮" in actual_data:
                print(f"  🔘 类型: 按钮事件")
                
            else:
                print(f"  ℹ️ 类型: 其他信息")
        
        print("-" * 30)

def test_key_mapping():
    """测试按键映射"""
    print("\n🎯 测试按键映射")
    print("=" * 50)
    
    key_mapping = {
        "摇杆：上": "w",
        "摇杆：下": "s", 
        "摇杆：左": "a",
        "摇杆：右": "d",
        "摇杆：左上": ["w", "a"],
        "摇杆：右上": ["w", "d"],
        "摇杆按键按下": "space",
        "E 按钮按下": "e",
    }
    
    test_actions = ["摇杆：上", "摇杆：左上", "摇杆按键按下", "E 按钮按下"]
    
    for action in test_actions:
        if action in key_mapping:
            keys = key_mapping[action]
            if isinstance(keys, list):
                keys_str = " + ".join(keys)
            else:
                keys_str = keys
            print(f"✅ {action} -> {keys_str}")
        else:
            print(f"❌ {action} -> 未映射")

def main():
    test_data_parsing()
    test_key_mapping()
    
    print("\n✅ 测试完成!")
    print("\n📋 使用说明:")
    print("1. 运行 joystick_controller.py 启动基础版")
    print("2. 运行 advanced_controller.py 启动增强版")
    print("3. 确保以管理员权限运行")

if __name__ == "__main__":
    main()
