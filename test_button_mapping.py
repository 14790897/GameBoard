#!/usr/bin/env python3
"""
按键映射测试脚本
用于验证按键映射是否正确工作
"""

import time
from collections import defaultdict

class ButtonMappingTest:
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
        
    def test_mapping(self):
        """测试按键映射"""
        print("🧪 按键映射测试开始...")
        print("=" * 50)
        
        # 测试按钮事件
        button_events = [
            "上按钮按下",
            "下按钮按下", 
            "左按钮按下",
            "右按钮按下",
            "摇杆按键按下",
            "E 按钮按下",
            "F 按钮按下"
        ]
        
        for event in button_events:
            print(f"\n📋 测试事件: {event}")
            
            # 检查是否在映射中
            if event in self.key_mapping:
                keys = self.key_mapping[event]
                print(f"✅ 映射存在: {event} -> {keys}")
                
                # 检查防抖逻辑
                should_process = self.should_process_button_event(event)
                print(f"🔄 防抖检查: {should_process}")
                
                if should_process:
                    # 模拟按键处理
                    if keys:
                        self.simulate_press_keys(keys, event)
                    else:
                        print("⚠️  按键映射为空或None")
                else:
                    print("🚫 防抖阻止处理")
            else:
                print(f"❌ 映射不存在: {event}")
                
        print("\n" + "=" * 50)
        print("🧪 测试完成!")
    
    def should_process_button_event(self, button_data):
        """判断是否应该处理按钮事件（防抖）"""
        current_time = time.time()
        last_time = self.last_button_time.get(button_data, 0)
        
        # 如果距离上次触发的时间超过防抖时间，则允许处理
        return current_time - last_time > self.button_debounce_time
    
    def simulate_press_keys(self, keys, event):
        """模拟按键处理（不实际按键）"""
        if isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            if not self.key_states[key]:
                # 模拟按键
                print(f"🔽 模拟按下: {key}")
                self.key_states[key] = True
            else:
                print(f"⚠️  按键已处于按下状态: {key}")
                
        # 更新按钮状态
        self.button_states[event] = True
        self.last_button_time[event] = time.time()
    
    def test_specific_events(self):
        """测试具体的问题事件"""
        print("\n🔍 问题事件专项测试...")
        print("=" * 50)
        
        problem_events = ["上按钮按下", "左按钮按下", "下按钮按下"]
        
        for event in problem_events:
            print(f"\n🧪 详细测试: {event}")
            
            # 步骤1：检查映射
            print(f"1️⃣ 检查映射: {event} in key_mapping = {event in self.key_mapping}")
            if event in self.key_mapping:
                keys = self.key_mapping[event]
                print(f"   映射值: {keys}")
                print(f"   映射类型: {type(keys)}")
                print(f"   映射为空: {not keys}")
            
            # 步骤2：检查防抖
            should_process = self.should_process_button_event(event)
            print(f"2️⃣ 防抖检查: {should_process}")
            
            # 步骤3：检查按键状态
            if event in self.key_mapping:
                keys = self.key_mapping[event]
                if keys:
                    if isinstance(keys, str):
                        keys = [keys]
                    for key in keys:
                        key_state = self.key_states[key]
                        print(f"3️⃣ 按键状态: {key} = {key_state}")
                        
            time.sleep(0.2)  # 稍作延迟避免防抖影响

if __name__ == "__main__":
    tester = ButtonMappingTest()
    tester.test_mapping()
    tester.test_specific_events()
