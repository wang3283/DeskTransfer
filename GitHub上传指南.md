# 📤 GitHub在线构建指南

## 🎯 目标：5分钟内获得Windows exe文件

这个指南帮你在没有Python的Windows环境下获得DeskTransfer的exe文件！

---

## 🚀 步骤1：注册GitHub账户

1. 访问 [github.com](https://github.com)
2. 点击右上角 **Sign up**
3. 按提示注册账户（免费）

---

## 🚀 步骤2：创建新仓库

1. 登录后，点击右上角 **+** → **New repository**
2. 仓库名称：`desktransfer` 或任意名称
3. 描述：`局域网图片传输工具`（可选）
4. 保持 **Public**（公开）
5. **不要**勾选 "Add a README file"
6. 点击 **Create repository**

---

## 🚀 步骤3：上传项目文件

### 方法A：网页上传（推荐）

1. 在新仓库页面，点击 **uploading an existing file**
2. 将整个DeskTransfer文件夹内的**所有文件**拖拽到网页上
3. 或者逐个点击选择文件上传
4. 上传完成后，点击 **Commit changes**

### 方法B：命令行上传（高级用户）

```bash
# 安装Git（可选）
# 下载：https://git-scm.com/downloads

# 初始化并上传
git init
git add .
git commit -m "上传DeskTransfer项目"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

---

## 🚀 步骤4：触发在线构建

1. 在仓库页面点击 **Actions** 标签
2. 点击左侧 **Build Windows Executables**
3. 点击右侧 **Run workflow** 按钮
4. 确认后点击 **Run workflow**

> 💡 **Actions** 首次使用可能需要启用，点击 **I understand...** 启用

---

## 🚀 步骤5：等待构建完成

- 构建需要 **5-10分钟**
- 页面会显示构建进度
- 成功后显示 ✅ **completed**

---

## 🚀 步骤6：下载exe文件

1. 点击成功的构建记录
2. 滚动到底部，点击 **Artifacts**
3. 点击 **DeskTransfer-Windows** 下载ZIP文件
4. 解压后直接使用！

---

## 📁 获得的文件

解压后你将获得：
- `DeskTransfer-Sender.exe` - 发送端程序
- `DeskTransfer-Receiver.exe` - 接收端程序
- `start.bat` - 双击启动菜单
- `README.txt` - 使用说明
- `data/` - 数据文件夹

---

## 🎉 完成！

现在你可以：
- 双击 `start.bat` 选择启动程序
- 或直接运行 `DeskTransfer-Sender.exe` / `DeskTransfer-Receiver.exe`
- 程序完全独立，无需安装Python！

---

## ❓ 遇到问题？

### Actions不可用
- 确保仓库是 **Public**（公开）
- 或者升级到GitHub Pro（付费）

### 构建失败
- 检查是否所有文件都上传了
- 重新上传 `.github/workflows/build-windows.yml` 文件

### 无法下载
- 使用Chrome浏览器
- 或者复制下载链接用其他工具下载

---

## 💡 提示

- 每个月有2000分钟的免费Actions时间
- 构建一次大约用5分钟
- 可以多次构建不同版本

**享受你的DeskTransfer工具吧！** 🎊
