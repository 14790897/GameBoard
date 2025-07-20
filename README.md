# 🎮 JoystickShield PC 控制器

基于 Arduino JoystickShield 的 PC 游戏控制器，支持摇杆方向控制和按钮映射。

## 🚀 快速开始

### 1. 硬件准备
- Arduino Uno/Nano
- JoystickShield 扩展板
- USB 数据线

### 2. 软件安装
```bash
pip install pyserial keyboard pywin32
```

### 3. 上传 Arduino 代码
使用 PlatformIO 或 Arduino IDE 上传 `src/main.cpp` 到开发板

### 4. 运行控制器
```bash
# 直接运行
python joystick_controller_final.py

# 或使用启动脚本
start_joystick.bat
```

## 🎯 功能特性

### 摇杆控制（长按模式）
- **上/下/左/右** → 持续按住 WASD 键
- **对角线移动** → 同时按住两个方向键
- **回中自动释放** → 摇杆回中时自动释放所有方向键

### 按钮功能
- **短按**: 快速按下释放，触发对应功能键
- **长按**: 按住0.5秒以上，触发长按功能

### 按键映射
```
摇杆方向:  上→W  下→S  左→A  右→D
短按功能:  摇杆按键→F  上按钮→O  下按钮→J  左按钮→I  右按钮→K
长按功能:  摇杆按键→空格  方向按钮→方向键  E→Shift  F→Ctrl
```

## 🔧 技术特点

- **多输入方法支持**: Win32 API / keyboard 库 / pynput 库
- **自动端口检测**: 智能识别 Arduino 端口
- **游戏兼容性优化**: 支持大多数 PC 游戏
- **实时响应**: 10ms 轮询间隔，低延迟控制

## ⚠️ 使用提示

1. **游戏窗口**: 确保游戏窗口处于活动状态
2. **管理员权限**: 某些游戏需要以管理员身份运行程序
3. **窗口模式**: 建议将游戏设置为窗口化模式以获得最佳兼容性

## 📁 项目结构

```
GameBoard/
├── src/main.cpp                    # Arduino 代码
├── joystick_controller_final.py    # PC 控制器程序
├── start_joystick.bat              # 启动脚本
├── platformio.ini                  # PlatformIO 配置
└── README.md                       # 项目说明
``` Controller

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
