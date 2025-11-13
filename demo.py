#!/usr/bin/env python3
"""
DeskTransfer 演示脚本
演示如何使用DeskTransfer进行图片传输
"""
import os
import sys
import time
import subprocess
from PIL import Image, ImageDraw, ImageFont

def create_demo_images():
    """创建演示用的图片"""
    print("创建演示图片...")
    
    # 创建演示图片目录
    demo_dir = "demo_images"
    os.makedirs(demo_dir, exist_ok=True)
    
    # 创建几个演示图片
    images_info = [
        ("demo1.jpg", "DeskTransfer", "图片传输工具", (255, 100, 100)),
        ("demo2.jpg", "局域网", "快速传输", (100, 255, 100)),
        ("demo3.jpg", "批量处理", "多文件支持", (100, 100, 255))
    ]
    
    for filename, title, subtitle, color in images_info:
        # 创建图片
        img = Image.new('RGB', (400, 300), color)
        draw = ImageDraw.Draw(img)
        
        # 添加文本
        try:
            # 尝试使用系统字体
            font_title = ImageFont.truetype("Arial.ttf", 36)
            font_subtitle = ImageFont.truetype("Arial.ttf", 24)
        except:
            # 如果找不到字体，使用默认字体
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
        
        # 计算文本位置
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
        
        title_x = (400 - title_width) // 2
        title_y = 100
        subtitle_x = (400 - subtitle_width) // 2
        subtitle_y = 180
        
        # 绘制文本
        draw.text((title_x, title_y), title, fill="white", font=font_title)
        draw.text((subtitle_x, subtitle_y), subtitle, fill="white", font=font_subtitle)
        
        # 保存图片
        img.save(os.path.join(demo_dir, filename))
        print(f"已创建: {filename}")
    
    print("演示图片创建完成!")
    return demo_dir

def show_usage_guide():
    """显示使用指南"""
    print("\n" + "="*50)
    print("DeskTransfer 使用演示")
    print("="*50)
    print("\n1. 启动接收端:")
    print("   python receiver.py")
    print("\n2. 启动发送端:")
    print("   python sender.py")
    print("\n3. 在发送端中:")
    print("   - 输入接收端IP地址")
    print("   - 点击'选择文件'，选择演示图片")
    print("   - 点击'连接'按钮")
    print("   - 点击'发送文件'开始传输")
    print("\n4. 查看传输结果:")
    print("   接收的文件保存在 data/received/ 目录中")
    print("\n" + "="*50)

def main():
    """主函数"""
    print("DeskTransfer 演示程序")
    print("="*30)
    
    # 创建演示图片
    demo_dir = create_demo_images()
    
    # 显示使用指南
    show_usage_guide()
    
    # 询问是否启动应用程序
    print("\n是否要启动接收端和发送端进行演示? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y' or choice == 'yes':
        print("\n正在启动接收端...")
        receiver_process = subprocess.Popen([sys.executable, "receiver.py"])
        
        time.sleep(2)  # 等待接收端启动
        
        print("正在启动发送端...")
        sender_process = subprocess.Popen([sys.executable, "sender.py"])
        
        print("\n两个应用程序已启动!")
        print("请按照上述使用指南进行操作")
        print("\n按Enter键关闭应用程序...")
        input()
        
        # 关闭应用程序
        receiver_process.terminate()
        sender_process.terminate()
        print("应用程序已关闭")
    
    print("\n演示完成!")
    print(f"演示图片保存在 {demo_dir} 目录中")

if __name__ == "__main__":
    main()