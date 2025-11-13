#!/usr/bin/env python3
"""
DeskTransfer 发送端主程序
启动发送端应用程序
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.sender_ui import SenderUI

def main():
    """主函数"""
    try:
        # 创建主窗口
        root = TkinterDnD.Tk()
        
        # 设置窗口图标（如果有的话）
        try:
            # 可以在这里设置应用图标
            # root.iconbitmap("icon.ico")
            pass
        except:
            pass
        
        # 创建应用实例
        app = SenderUI(root)
        
        # 运行主循环
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("错误", f"应用程序启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()