# JoystickShield PC 控制器使用说明

## 📋 项目概述

这是一个完整的 JoystickShield 到 PC 键盘控制解决方案，包含：

- Arduino 端摇杆检测代码
- Python 端串口监听和键盘模拟
- 多种游戏配置模式
- 热键切换和自定义映射

## 🔧 安装步骤

### 1. 硬件连接
```
摇杆 X 轴  -> Arduino A0
摇杆 Y 轴  -> Arduino A1  
摇杆按键  -> Arduino 引脚 8
上按钮    -> Arduino 引脚 2
右按钮    -> Arduino 引脚 3
下按钮    -> Arduino 引脚 4
左按钮    -> Arduino 引脚 5
E 按钮    -> Arduino 引脚 6
F 按钮    -> Arduino 引脚 7
VCC       -> Arduino 5V
GND       -> Arduino GND
```

### 2. Arduino 代码上传
1. 打开 `src/main.cpp`
2. 使用 PlatformIO 或 Arduino IDE 上传到开发板
3. 确保串口波特率设置为 115200

### 3. Python 环境配置
```bash
# 方法1: 运行自动安装脚本
install.bat

# 方法2: 手动安装
pip install pyserial keyboard
```

### 4. 串口配置
- **优先串口**: 程序会优先尝试连接 **COM13**
- **自动检测**: 如果 COM13 不可用，会自动检测其他串口
- **手动选择**: 如果自动检测失败，可以手动选择串口

> 💡 **提示**: 如果你的 Arduino 使用其他串口，程序会自动处理，无需手动修改代码

## 🎮 使用方法

### 启动控制器
```bash
# 方法1: 使用启动器
start.bat

# 方法2: 直接运行
python advanced_controller.py
```

### 游戏配置模式

#### 1. FPS 游戏模式 (默认)
- 摇杆方向 -> WASD 移动
- 摇杆按键 -> 空格键 (跳跃)
- 上按钮 -> R (换弹)
- 下按钮 -> C (蹲下)
- 左按钮 -> Shift (奔跑)
- 右按钮 -> Ctrl (慢走)
- E/F 按钮 -> E/F 键

#### 2. 方向键模式
- 摇杆方向 -> 方向键
- 摇杆按键 -> 回车键
- 其他按钮 -> WASD + Esc/Tab

#### 3. 多媒体控制模式
- 摇杆上/下 -> 音量+/-
- 摇杆左/右 -> 上一首/下一首
- 摇杆按键 -> 播放/暂停
- E 按钮 -> 静音
- F 按钮 -> 停止

#### 4. 自定义模式
- 可在代码中自定义按键映射

### 热键控制
- `Ctrl + Shift + P`: 切换游戏配置
- `Ctrl + C`: 退出程序

## 📁 文件结构

```
GameBoard/
├── src/
│   └── main.cpp                 # Arduino 代码
├── joystick_controller.py       # 基础版控制器
├── advanced_controller.py       # 增强版控制器
├── config.txt                   # 配置文件
├── install.bat                  # 安装脚本
├── start.bat                    # 启动脚本
├── platformio.ini              # PlatformIO 配置
└── README.md                   # 使用说明
```

## ⚙️ 高级配置

### 自定义按键映射
编辑 `advanced_controller.py` 中的 `game_profiles` 部分：

```python
GameProfile(
    name="我的游戏",
    key_mapping={
        "摇杆：上": "w",
        "摇杆按键按下": "space",
        # ... 更多映射
    },
    description="自定义游戏配置"
)
```

### 串口设置
如果需要修改串口设置，在代码中修改：
```python
controller.connect_serial(port="COM3", baudrate=115200)
```

## 🔍 故障排除

### 常见问题

#### 1. 串口连接失败
- 检查 Arduino 是否正确连接
- 确认串口号是否正确
- 检查是否有其他程序占用串口

#### 2. 按键不响应
- 确保以管理员身份运行 Python 程序
- 检查 keyboard 库是否正确安装
- 验证按键映射是否正确

#### 3. 摇杆漂移
- 重新校准摇杆 (`joystickShield.calibrateJoystick()`)
- 调整死区阈值
- 检查硬件连接

#### 4. 权限错误
```bash
# Windows: 以管理员身份运行
# Linux: 添加用户到 dialout 组
sudo usermod -a -G dialout $USER
```

### 调试模式
在代码中启用详细输出：
```python
# 显示所有串口数据
print(f"📡 接收: {data}")

# 显示按键状态
print(f"🔽 按下: {key}")
print(f"🔼 释放: {key}")
```

## 🎯 游戏兼容性

### 已测试游戏
- ✅ CS:GO / CS2
- ✅ Minecraft
- ✅ 任意支持键盘输入的游戏

### 推荐设置
- **FPS 游戏**: 使用 FPS 模式
- **RPG 游戏**: 使用方向键模式
- **媒体播放**: 使用多媒体模式

## 📚 扩展功能

### 添加新游戏配置
```python
new_profile = GameProfile(
    name="新游戏",
    key_mapping={
        # 你的按键映射
    },
    description="游戏描述"
)
self.game_profiles.append(new_profile)
```

### 添加鼠标控制
```python
import mouse

# 摇杆控制鼠标移动
if x_pos != 0 or y_pos != 0:
    mouse.move(x_pos * sensitivity, y_pos * sensitivity, absolute=False)
```

### 添加宏功能
```python
def execute_macro():
    keyboard.press('ctrl')
    keyboard.press('c')
    time.sleep(0.1)
    keyboard.release('c')
    keyboard.release('ctrl')
```

## 📧 技术支持

如有问题，请检查：
1. 硬件连接是否正确
2. 依赖库是否安装完整
3. 是否以管理员权限运行
4. Arduino 代码是否正确上传

## 📄 许可证

本项目基于 MIT 许可证开源。 Controller

基于 Arduino 的游戏手柄控制器项目，使用 JoystickShield 库来处理摇杆和按钮输入。

## 功能特性

- **摇杆控制**: 支持 8 方向检测（上、下、左、右、右上、右下、左上、左下）
- **按钮支持**: 7 个按钮（摇杆按键 K + 方向按钮 A/B/C/D + 扩展按钮 E/F）
- **自动校准**: 启动时自动校准摇杆中心位置
- **防抖处理**: 内置按钮防抖功能
- **多种模式**: 演示模式、游戏模式、调试模式
- **性能监控**: 实时 FPS 和内存使用监控

## 硬件连接

### 默认引脚配置

| 组件 | 引脚 | 说明 |
|------|------|------|
| 摇杆 X 轴 | A0 | 模拟输入 |
| 摇杆 Y 轴 | A1 | 模拟输入 |
| 摇杆按键 K | 8 | 数字输入（内部上拉） |
| 按钮 A (上) | 2 | 数字输入（内部上拉） |
| 按钮 B (右) | 3 | 数字输入（内部上拉） |
| 按钮 C (下) | 4 | 数字输入（内部上拉） |
| 按钮 D (左) | 5 | 数字输入（内部上拉） |
| 按钮 E | 6 | 数字输入（内部上拉） |
| 按钮 F | 7 | 数字输入（内部上拉） |

### 自定义引脚

如果需要使用不同的引脚，可以在 `setup()` 函数中调用：

```cpp
// 设置摇杆引脚
joystickShield.setJoystickPins(A2, A3);

// 设置按钮引脚 (K, A, B, C, D, F, E)
joystickShield.setButtonPins(9, 10, 11, 12, 13, A4, A5);
```

## 软件使用

### 基本使用

```cpp
#include <JoystickShield.h>

JoystickShield joystick;

void setup() {
    Serial.begin(115200);
    joystick.calibrateJoystick();
}

void loop() {
    joystick.processEvents();  // 必须调用
    
    // 检测摇杆方向
    if (joystick.isUp()) {
        Serial.println("向上");
    }
    
    // 检测按钮
    if (joystick.isUpButton()) {
        Serial.println("A 按钮被按下");
    }
    
    delay(100);
}
```

### 操作模式

程序支持三种操作模式，按 F 按钮切换：

1. **演示模式 (DEMO_MODE)**: 显示所有输入的详细信息
2. **游戏模式 (GAME_MODE)**: 简化输出，适合游戏使用
3. **调试模式 (DEBUG_MODE)**: 显示详细的调试信息和性能数据

### API 参考

#### 初始化方法
- `calibrateJoystick()`: 校准摇杆中心位置
- `setJoystickPins(xPin, yPin)`: 设置摇杆引脚
- `setButtonPins(k, a, b, c, d, f, e)`: 设置按钮引脚
- `setDeadZone(zone)`: 设置摇杆死区

#### 事件处理
- `processEvents()`: 处理输入事件（必须在主循环中调用）

#### 摇杆检测
- `isUp()`, `isDown()`, `isLeft()`, `isRight()`: 4 方向检测
- `isRightUp()`, `isRightDown()`, `isLeftUp()`, `isLeftDown()`: 对角线方向
- `isCenter()`, `isNotCenter()`: 中心位置检测

#### 按钮检测

**边沿检测（按下瞬间触发一次）**
- `isJoystickButton()`: 摇杆按键 K
- `isUpButton()`, `isRightButton()`, `isDownButton()`, `isLeftButton()`: A/B/C/D 按钮
- `isEButton()`, `isFButton()`: E/F 扩展按钮

**状态检测（按住期间持续返回true）**
- `isJoystickButtonPressed()`: 摇杆按键 K 状态
- `isUpButtonPressed()`, `isRightButtonPressed()`, `isDownButtonPressed()`, `isLeftButtonPressed()`: A/B/C/D 按钮状态
- `isEButtonPressed()`, `isFButtonPressed()`: E/F 扩展按钮状态

> **使用建议**:
> - 边沿检测适用于菜单选择、模式切换等一次性操作
> - 状态检测适用于游戏控制、连续移动等需要持续响应的场景

#### 数值读取
- `xAmplitude()`, `yAmplitude()`: 摇杆偏移量（相对于中心）
- `xRaw()`, `yRaw()`: 摇杆原始 ADC 值

#### 工具方法
- `printStatus()`: 打印当前状态
- `printCalibration()`: 打印校准信息

## 编译和上传

### 使用 PlatformIO

```bash
# 编译项目
pio run

# 上传到 Arduino
pio run --target upload

# 打开串口监视器
pio device monitor
```

### 运行测试

```bash
# 运行单元测试
pio test
```

## 项目结构

```
GameBoard/
├── include/
│   └── JoystickShield.h      # 库头文件
├── src/
│   ├── main.cpp              # 主程序
│   └── JoystickShield.cpp    # 库实现
├── test/
│   └── test_joystick.cpp     # 单元测试
├── platformio.ini            # PlatformIO 配置
└── README.md                 # 项目说明
```

## 故障排除

### 摇杆漂移
- 重新运行校准：`joystick.calibrateJoystick()`
- 调整死区：`joystick.setDeadZone(50)`

### 按钮无响应
- 检查引脚连接
- 确认按钮使用内部上拉电阻
- 检查防抖设置

### 串口输出异常
- 确认波特率设置为 115200
- 检查串口连接
- 重启 Arduino

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
