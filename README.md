# 🎮 JoystickShield PC 控制器

基于 Arduino JoystickShield 的 PC 游戏控制器，支持摇杆方向控制和按钮映射。

## 🚀 快速开始

### 方式一：下载可执行文件（推荐）

📥 **直接下载使用**：

1. 前往 [Releases 页面](../../releases) 下载最新版本
2. 下载 `GameBoard-v*.tar.gz` 压缩包
3. 解压后运行 `JoystickController.exe`

### 方式二：从源码运行

#### 1. 硬件准备

- Arduino Uno/Nano
- JoystickShield 扩展板
- USB 数据线

#### 2. 软件安装

```bash
pip install pyserial keyboard pywin32
```

#### 3. 上传 Arduino 代码

使用 PlatformIO 或 Arduino IDE 上传 `src/main.cpp` 到开发板

#### 4. 运行控制器

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

```text
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

```text
GameBoard/
├── src/main.cpp                    # Arduino 代码
├── joystick_controller_final.py    # PC 控制器程序
├── start_joystick.bat              # 启动脚本
├── platformio.ini                  # PlatformIO 配置
└── README.md                       # 项目说明
```

## 🔧 硬件连接

```text
摇杆 X 轴  -> Arduino A0    摇杆 Y 轴  -> Arduino A1
摇杆按键  -> Arduino 引脚 8  上按钮    -> Arduino 引脚 2
右按钮    -> Arduino 引脚 3  下按钮    -> Arduino 引脚 4
左按钮    -> Arduino 引脚 5  E 按钮    -> Arduino 引脚 6
F 按钮    -> Arduino 引脚 7  VCC       -> Arduino 5V
GND       -> Arduino GND
```

## 📄 许可证

MIT License
