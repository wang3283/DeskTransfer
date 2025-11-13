#!/usr/bin/env python3
"""
简单的图标生成脚本
为DeskTransfer创建基本的应用图标
"""
import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("需要安装Pillow库: pip install Pillow")
    exit(1)

def create_simple_icon():
    """创建简单的应用图标"""
    
    # 图标尺寸（Windows ico需要多个尺寸）
    sizes = [16, 32, 48, 64, 128, 256]
    
    # 创建assets目录
    assets_dir = Path('assets')
    assets_dir.mkdir(exist_ok=True)
    
    images = []
    
    for size in sizes:
        # 创建图像
        img = Image.new('RGBA', (size, size), (52, 152, 219, 255))  # 蓝色背景
        draw = ImageDraw.Draw(img)
        
        # 绘制边框
        border_width = max(1, size // 32)
        draw.rectangle(
            [border_width, border_width, size-border_width-1, size-border_width-1],
            outline=(255, 255, 255, 255),
            width=border_width
        )
        
        # 绘制简单的箭头或传输符号
        # 计算箭头大小
        arrow_size = size // 2
        center = size // 2
        
        # 绘制右箭头 (表示传输)
        arrow_points = [
            (center - arrow_size//4, center - arrow_size//3),  # 左上
            (center + arrow_size//4, center),                   # 右中
            (center - arrow_size//4, center + arrow_size//3),  # 左下
        ]
        draw.polygon(arrow_points, fill=(255, 255, 255, 255))
        
        # 绘制文字 "DT" (DeskTransfer缩写) - 仅在较大尺寸上
        if size >= 64:
            try:
                # 尝试使用系统字体
                font_size = size // 4
                try:
                    # Windows
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        # macOS
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
                    except:
                        # Linux
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                        except:
                            font = ImageFont.load_default()
                
                text = "DT"
                # 获取文字边界框
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算文字位置（左下角）
                text_x = border_width * 2
                text_y = size - text_height - border_width * 2
                
                # 绘制文字
                draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
            except Exception as e:
                print(f"警告: 无法添加文字到{size}x{size}图标: {e}")
        
        images.append(img)
    
    # 保存为ico文件（包含多个尺寸）
    icon_path = assets_dir / 'icon.ico'
    images[0].save(
        icon_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )
    
    print(f"✓ 图标已创建: {icon_path}")
    
    # 也保存为PNG（用于文档或其他用途）
    png_path = assets_dir / 'icon.png'
    images[-1].save(png_path, format='PNG')
    print(f"✓ PNG版本已创建: {png_path}")
    
    return icon_path

def create_sender_receiver_icons():
    """为发送端和接收端创建不同的图标"""
    
    assets_dir = Path('assets')
    assets_dir.mkdir(exist_ok=True)
    
    size = 256
    
    # 发送端图标（红色，向右箭头）
    sender_img = Image.new('RGBA', (size, size), (231, 76, 60, 255))  # 红色
    draw = ImageDraw.Draw(sender_img)
    
    # 边框
    border_width = size // 32
    draw.rectangle(
        [border_width, border_width, size-border_width-1, size-border_width-1],
        outline=(255, 255, 255, 255),
        width=border_width
    )
    
    # 向右箭头（发送）
    center = size // 2
    arrow_size = size // 3
    arrow_points = [
        (center - arrow_size, center - arrow_size//2),
        (center + arrow_size, center),
        (center - arrow_size, center + arrow_size//2),
    ]
    draw.polygon(arrow_points, fill=(255, 255, 255, 255))
    
    sender_path = assets_dir / 'sender_icon.png'
    sender_img.save(sender_path, format='PNG')
    print(f"✓ 发送端图标已创建: {sender_path}")
    
    # 接收端图标（绿色，向左箭头）
    receiver_img = Image.new('RGBA', (size, size), (46, 204, 113, 255))  # 绿色
    draw = ImageDraw.Draw(receiver_img)
    
    # 边框
    draw.rectangle(
        [border_width, border_width, size-border_width-1, size-border_width-1],
        outline=(255, 255, 255, 255),
        width=border_width
    )
    
    # 向左箭头（接收）
    arrow_points = [
        (center + arrow_size, center - arrow_size//2),
        (center - arrow_size, center),
        (center + arrow_size, center + arrow_size//2),
    ]
    draw.polygon(arrow_points, fill=(255, 255, 255, 255))
    
    receiver_path = assets_dir / 'receiver_icon.png'
    receiver_img.save(receiver_path, format='PNG')
    print(f"✓ 接收端图标已创建: {receiver_path}")

def main():
    """主函数"""
    print("=" * 50)
    print("DeskTransfer 图标生成工具")
    print("=" * 50)
    print()
    
    try:
        # 创建主图标
        print("正在创建应用图标...")
        icon_path = create_simple_icon()
        print()
        
        # 创建发送端和接收端图标
        print("正在创建发送端和接收端图标...")
        create_sender_receiver_icons()
        print()
        
        print("=" * 50)
        print("所有图标创建完成！")
        print("=" * 50)
        print()
        print("图标位置: assets/")
        print("  - icon.ico (Windows图标)")
        print("  - icon.png (PNG版本)")
        print("  - sender_icon.png (发送端)")
        print("  - receiver_icon.png (接收端)")
        print()
        print("提示: 重新打包程序后，图标将自动应用到exe文件")
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
