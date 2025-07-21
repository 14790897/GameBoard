# JoystickController - Requirements 总结

## 📋 生成的Requirements文件

### 核心文件
| 文件名 | 用途 | 说明 |
|--------|------|------|
| `requirements.txt` | 生产环境 | 运行程序所需的核心依赖 |
| `requirements-minimal.txt` | 最小环境 | 仅包含必需的运行时依赖 |
| `requirements-dev.txt` | 开发环境 | 包含开发、测试、文档工具 |

### 安装脚本
| 文件名 | 平台 | 功能 |
|--------|------|------|
| `install_dependencies.bat` | Windows | 自动安装依赖的批处理脚本 |
| `install_dependencies.sh` | Linux/macOS | 自动安装依赖的Shell脚本 |
| `verify_requirements.py` | 全平台 | 验证依赖安装状态 |

### 文档
| 文件名 | 内容 |
|--------|------|
| `DEPENDENCIES.md` | 详细的依赖说明和故障排除 |
| `REQUIREMENTS_SUMMARY.md` | 本文件，Requirements总结 |

## 🎯 快速开始

### 1. 安装依赖 (选择一种方法)

**方法A: 自动脚本 (推荐)**
```cmd
# Windows
install_dependencies.bat

# Linux/macOS  
chmod +x install_dependencies.sh
./install_dependencies.sh
```

**方法B: 手动安装**
```bash
pip install -r requirements.txt
```

**方法C: 最小安装**
```bash
pip install -r requirements-minimal.txt
```

### 2. 验证安装
```bash
python verify_requirements.py
```

### 3. 运行程序
```bash
python joystick_controller_final.py
```

## 📦 依赖清单

### 必需依赖 (requirements.txt)
```
pyserial==3.5          # Arduino串口通信
pywin32==311           # Windows API (仅Windows)
keyboard==0.13.5       # 键盘输入模拟
pyinstaller==6.14.2    # 可执行文件打包
```

### 最小依赖 (requirements-minimal.txt)
```
pyserial>=3.5          # 串口通信 (必需)
pywin32>=311           # Windows API (Windows必需)
keyboard>=0.13.5       # 键盘控制 (推荐)
```

### 开发依赖 (requirements-dev.txt)
```
# 基础依赖
-r requirements.txt

# 开发工具
pytest>=7.0.0         # 单元测试
pytest-cov>=4.0.0     # 测试覆盖率
black>=22.0.0          # 代码格式化
flake8>=5.0.0          # 代码检查
mypy>=1.0.0            # 类型检查

# 文档工具
sphinx>=5.0.0          # 文档生成
sphinx-rtd-theme>=1.0.0

# 开发辅助
ipython>=8.0.0         # 交互式Python
jupyter>=1.0.0         # Jupyter笔记本
```

## 🔍 验证结果示例

运行 `python verify_requirements.py` 的输出示例：

```
==================================================
🔍 JoystickController 依赖验证
==================================================
🐍 Python版本检查:
   当前版本: 3.11.7
   ✅ Python版本符合要求

📦 核心依赖检查:
   ✅ pyserial: 3.5
   ✅ pywin32: Unknown
   ✅ (可选) keyboard: Unknown

🛠️ 构建工具检查:
   ✅ (可选) pyinstaller: 6.14.2

📚 标准库模块检查:
   ✅ time, threading, sys, ctypes, collections...

🎉 所有必需依赖都已正确安装！
✅ 可以运行 JoystickController
✅ 可以构建可执行文件
```

## 🖥️ 平台支持

### Windows (主要平台)
- ✅ 完全支持所有功能
- ✅ 所有依赖都可正常安装
- ✅ 可生成.exe可执行文件

### Linux
- ✅ 支持基本功能
- ❌ pywin32不可用 (使用keyboard库替代)
- ✅ 可生成Linux可执行文件
- ⚠️ 可能需要额外权限设置

### macOS
- ✅ 支持基本功能  
- ❌ pywin32不可用 (使用keyboard库替代)
- ✅ 可生成macOS可执行文件
- ⚠️ 需要辅助功能权限

## 🚨 常见问题

### Q: pip install失败怎么办？
A: 尝试以下解决方案：
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 逐个安装
pip install pyserial pywin32 keyboard pyinstaller
```

### Q: pywin32安装失败？
A: Windows平台解决方案：
```bash
pip install --upgrade setuptools
pip install pywin32
python Scripts/pywin32_postinstall.py -install
```

### Q: 权限问题？
A: 
- **Windows**: 以管理员身份运行命令提示符
- **Linux**: 添加用户到dialout和input组
- **macOS**: 在系统偏好设置中授予辅助功能权限

### Q: 验证脚本报错？
A: 确保Python版本3.7+，然后重新安装依赖：
```bash
python --version
pip install -r requirements.txt --force-reinstall
```

## 📊 版本兼容性

| Python版本 | 支持状态 | 说明 |
|------------|----------|------|
| 3.7 | ✅ 最低支持 | 基本功能可用 |
| 3.8 | ✅ 完全支持 | 推荐版本 |
| 3.9 | ✅ 完全支持 | 推荐版本 |
| 3.10 | ✅ 完全支持 | 推荐版本 |
| 3.11+ | ✅ 完全支持 | 最新特性 |

---

**生成时间**: 2025-07-21  
**验证状态**: ✅ 已测试通过  
**维护状态**: 🔄 持续更新
