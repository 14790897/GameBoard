# JoystickController - 依赖说明文档

## 📋 依赖概览

本项目需要以下Python包来正常运行：

### 🔧 核心依赖 (必需)

| 包名 | 版本 | 用途 | 平台 |
|------|------|------|------|
| `pyserial` | 3.5+ | Arduino串口通信 | 全平台 |
| `pywin32` | 311+ | Windows API调用 | 仅Windows |
| `keyboard` | 0.13.5+ | 键盘输入模拟 | 全平台 |

### 🛠️ 构建工具 (可选)

| 包名 | 版本 | 用途 |
|------|------|------|
| `pyinstaller` | 6.14.2+ | 打包成可执行文件 |

## 📦 Requirements文件说明

### `requirements.txt`
- **用途**: 生产环境的核心依赖
- **安装**: `pip install -r requirements.txt`
- **包含**: 运行程序所需的最小依赖集

### `requirements-minimal.txt`
- **用途**: 最小化运行时依赖
- **安装**: `pip install -r requirements-minimal.txt`
- **包含**: 仅核心功能所需的包

### `requirements-dev.txt`
- **用途**: 开发环境的完整依赖
- **安装**: `pip install -r requirements-dev.txt`
- **包含**: 开发、测试、文档生成工具

## 🚀 安装方法

### 方法1: 自动安装脚本 (推荐)

**Windows:**
```cmd
install_dependencies.bat
```

**Linux/macOS:**
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### 方法2: 手动安装

**基础安装:**
```bash
pip install -r requirements.txt
```

**最小安装:**
```bash
pip install -r requirements-minimal.txt
```

**开发环境:**
```bash
pip install -r requirements-dev.txt
```

### 方法3: 逐个安装

```bash
# 核心依赖
pip install pyserial>=3.5
pip install pywin32>=311  # 仅Windows
pip install keyboard>=0.13.5

# 构建工具
pip install pyinstaller>=6.14.2
```

## 🔍 依赖详细说明

### pyserial
- **功能**: 提供串口通信功能
- **用途**: 与Arduino设备进行数据交换
- **必需性**: ✅ 必需
- **替代方案**: 无

### pywin32
- **功能**: Windows API访问
- **用途**: 键盘输入模拟、窗口管理、输入法切换
- **必需性**: ✅ Windows平台必需
- **替代方案**: ctypes (功能有限)

### keyboard
- **功能**: 跨平台键盘控制
- **用途**: 键盘输入模拟的备用方案
- **必需性**: ⚠️ 推荐 (作为pywin32的备用)
- **替代方案**: pynput

### pyinstaller
- **功能**: Python程序打包
- **用途**: 生成独立可执行文件
- **必需性**: ❌ 可选 (仅构建时需要)
- **替代方案**: cx_Freeze, py2exe

## 🖥️ 平台兼容性

### Windows (主要支持平台)
- ✅ pyserial: 完全支持
- ✅ pywin32: 完全支持
- ✅ keyboard: 完全支持
- ✅ pyinstaller: 完全支持

### Linux
- ✅ pyserial: 完全支持
- ❌ pywin32: 不支持 (Windows专用)
- ✅ keyboard: 完全支持
- ✅ pyinstaller: 完全支持

### macOS
- ✅ pyserial: 完全支持
- ❌ pywin32: 不支持 (Windows专用)
- ⚠️ keyboard: 需要额外权限设置
- ✅ pyinstaller: 完全支持

## 🔧 故障排除

### 常见安装问题

**1. pywin32安装失败**
```bash
# 解决方案
pip install --upgrade setuptools
pip install pywin32
```

**2. keyboard权限问题 (Linux/macOS)**
```bash
# Linux: 添加用户到input组
sudo usermod -a -G input $USER

# macOS: 在系统偏好设置中授予辅助功能权限
```

**3. pyserial权限问题 (Linux)**
```bash
# 添加用户到dialout组
sudo usermod -a -G dialout $USER
```

**4. 网络问题**
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 📊 版本兼容性

### Python版本要求
- **最低版本**: Python 3.7
- **推荐版本**: Python 3.9+
- **测试版本**: Python 3.11.7

### 依赖版本策略
- **固定版本**: 生产环境使用确切版本
- **最低版本**: 开发环境使用最低兼容版本
- **定期更新**: 每月检查依赖更新

---

**更新时间**: 2025-07-21  
**维护状态**: ✅ 活跃维护
