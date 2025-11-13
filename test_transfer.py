#!/usr/bin/env python3
"""
测试脚本 - 模拟发送端功能
"""
import os
import sys
import socket
import struct
import time

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.protocol import *
from common.utils import get_local_ip, validate_ip_address

def test_file_transfer():
    """测试文件传输功能"""
    # 获取本机IP地址作为接收端地址
    receiver_ip = get_local_ip()
    print(f"连接到接收端: {receiver_ip}:{PORT}")
    
    # 测试图片文件
    test_files = [
        'test_images/red_square.jpg',
        'test_images/green_square.jpg',
        'test_images/blue_square.jpg'
    ]
    
    try:
        # 创建socket连接
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((receiver_ip, PORT))
        print("已连接到接收端")
        
        # 发送握手消息
        handshake = HandshakeMessage(client_name="Test Sender")
        client_socket.send(pack_message(handshake))
        print("已发送握手消息")
        
        # 接收握手响应
        data = client_socket.recv(HEADER_SIZE)
        msg_len = struct.unpack('!I', data[:HEADER_SIZE])[0]
        msg_data = client_socket.recv(msg_len)
        response = ProtocolMessage.from_json(msg_data.decode('utf-8'))
        
        if response.msg_type != MSG_TYPE_HANDSHAKE:
            print(f"无效的握手响应: {response.msg_type}")
            return
        
        print(f"握手成功，接收端: {response.client_name}")
        
        # 发送文件
        file_count = len(test_files)
        for i, file_path in enumerate(test_files):
            filename = os.path.basename(file_path)
            filesize = os.path.getsize(file_path)
            
            print(f"发送文件 {i+1}/{file_count}: {filename} ({filesize} 字节)")
            
            # 发送文件信息
            file_info = FileInfoMessage(
                filename=filename,
                filesize=filesize,
                file_count=file_count,
                current_file=i+1
            )
            client_socket.send(pack_message(file_info))
            
            # 发送文件数据
            with open(file_path, 'rb') as f:
                chunk_size = BUFFER_SIZE
                sent_bytes = 0
                
                while sent_bytes < filesize:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    file_data = FileDataMessage(data=chunk)
                    client_socket.send(pack_message(file_data))
                    
                    sent_bytes += len(chunk)
                    progress = int((sent_bytes / filesize) * 100)
                    print(f"\r传输进度: {progress}%", end="")
            
            print(f"\n文件 {filename} 发送完成")
            
            # 发送文件结束消息
            file_end = FileEndMessage()
            client_socket.send(pack_message(file_end))
            
            time.sleep(0.5)  # 短暂延迟，确保接收端处理完成
        
        # 发送批量传输结束消息
        batch_end = BatchEndMessage()
        client_socket.send(pack_message(batch_end))
        print("所有文件发送完成")
        
        # 关闭连接
        client_socket.close()
        print("连接已关闭")
        
    except Exception as e:
        print(f"传输过程中出错: {str(e)}")
        if 'client_socket' in locals():
            client_socket.close()

if __name__ == "__main__":
    print("开始测试文件传输...")
    test_file_transfer()
    print("测试完成")