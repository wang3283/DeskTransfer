#!/bin/bash

# DeskTransfer 启动脚本

echo "DeskTransfer - 局域网图片传输软件"
echo "=================================="
echo "1. 启动接收端"
echo "2. 启动发送端"
echo "3. 退出"
echo "=================================="

read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo "正在启动接收端..."
        python3 receiver.py
        ;;
    2)
        echo "正在启动发送端..."
        python3 sender.py
        ;;
    3)
        echo "退出程序"
        exit 0
        ;;
    *)
        echo "无效选择，请重新运行脚本"
        exit 1
        ;;
esac