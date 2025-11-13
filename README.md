# DeskTransfer - 局域网图片传输软件

这是一个简单的局域网图片传输软件，支持批量图片传输功能。

## 项目结构

```
desktransfer/
├── README.md              # 项目说明文档
├── requirements.txt       # Python依赖包列表
├── receiver.py           # 接收端应用程序
├── sender.py             # 发送端应用程序
├── common/               # 共享模块
│   ├── __init__.py
│   ├── protocol.py       # 通信协议定义
│   └── utils.py          # 工具函数
├── ui/                   # 用户界面模块
│   ├── __init__.py
│   ├── receiver_ui.py    # 接收端界面
│   └── sender_ui.py      # 发送端界面
└── data/                 # 数据存储目录
    ├── received/         # 接收的图片存储位置
    └── temp/             # 临时文件目录
```

## 功能特点

- 支持局域网内图片传输
- 支持批量选择和发送图片
- 简洁易用的图形界面
- 实时显示传输进度
- 支持常见图片格式（JPG, PNG, GIF等）

## 使用方法

### 方法一：使用源代码运行

1. 安装依赖：`pip install -r requirements.txt`
2. 在接收端电脑上运行 `receiver.py`
3. 在发送端电脑上运行 `sender.py`
4. 在发送端选择要发送的图片
5. 输入接收端的IP地址
6. 点击发送按钮开始传输

### 方法二：使用打包后的可执行文件（Windows）

**最简单的方式**：
1. 双击运行 **`一键打包.bat`** 进行打包（需要Python环境）
2. 打包完成后，在 `dist/DeskTransfer` 目录获得可执行文件
3. **重要**: 打包后的exe文件可以在**没有Python**的Windows电脑上直接运行！

**使用打包后的程序**：
1. 双击运行 `start.bat` 选择启动发送端或接收端
2. 或直接运行 `DeskTransfer-Sender.exe` 或 `DeskTransfer-Receiver.exe`
3. 按照界面提示进行操作

**详细文档**：
- 快速开始：[快速开始.md](快速开始.md)
- 打包说明：[Windows打包说明.md](Windows打包说明.md)
- 构建指南：[BUILD_GUIDE.md](BUILD_GUIDE.md)

## 🚀 在线构建Windows版本（推荐）

如果你的Windows电脑没有Python环境，可以使用GitHub在线构建服务：

### 方法一：自动构建（最简单）
1. **上传代码到GitHub**：
   - 访问 [GitHub.com](https://github.com)
   - 创建新仓库，上传整个DeskTransfer项目
   - 或者fork现有的仓库

2. **触发在线构建**：
   - 在GitHub仓库页面点击 **Actions** 标签
   - 点击 **Build Windows Executables**
   - 点击 **Run workflow** 按钮
   - 等待5-10分钟构建完成

3. **下载exe文件**：
   - 构建完成后，在Actions页面找到成功的运行
   - 点击 **Artifacts** 下载 `DeskTransfer-Windows` 压缩包
   - 解压后直接使用，无需安装Python！

### 方法二：手动触发（高级用户）
```bash
# 1. 上传项目到GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/desktransfer.git
git push -u origin main

# 2. 在GitHub上触发Actions
# 访问: https://github.com/YOUR_USERNAME/desktransfer/actions
```

### 📦 构建产物
- ✅ `DeskTransfer-Sender.exe` - 发送端程序
- ✅ `DeskTransfer-Receiver.exe` - 接收端程序
- ✅ `start.bat` - 启动菜单
- ✅ `README.txt` - 使用说明
- ✅ 便携版ZIP包 - 可直接分发

---

## 💻 本地构建Windows版本

如果你有Python环境的电脑，可以本地构建：

## Windows独立可执行文件

✅ **无需Python环境！** 打包后的程序可以在任何Windows 7+电脑上直接运行

### 打包工具
- `一键打包.bat` - 最简单的一键打包工具（推荐）
- `build_windows.py` - 增强版Python打包脚本
- `build_exe.py` - 原始打包脚本
- `build.bat` - Windows批处理打包脚本

### 打包后获得
- `DeskTransfer-Sender.exe` - 发送端独立可执行文件
- `DeskTransfer-Receiver.exe` - 接收端独立可执行文件
- `start.bat` - 启动菜单脚本
- `DeskTransfer_v1.0.0_Portable.zip` - 便携版压缩包

### 分发部署
将整个 `dist/DeskTransfer` 目录复制到任何Windows电脑，无需安装Python或任何依赖！

## 依赖包

**源代码运行时需要**（打包后无需安装）：
- Python 3.6+ 
- tkinter (通常随Python安装)
- Pillow (图像处理)
- socket (网络通信)
- tkinterdnd2 (拖放功能)
- requests (网络请求)
- psutil (系统信息)

**打包时需要**：
- PyInstaller (自动安装)# DeskTransfer
# DeskTransfer
