#!/usr/bin/env python3
"""
命令行版本的接收端 - 用于测试
"""
import os
import sys
import socket
import struct
import threading
import time
import json

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.protocol import *
from common.utils import get_local_ip

class CommandLineReceiver:
    """命令行版本的接收端"""
    
    def __init__(self):
        self.server_socket = None
        self.client_socket = None
        self.running = False
        self.save_dir = "data/received"
        
        # 确保保存目录存在
        os.makedirs(self.save_dir, exist_ok=True)
    
    def start_server(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((get_local_ip(), PORT))
            self.server_socket.listen(1)
            self.running = True
            
            print(f"服务器已启动，监听地址: {get_local_ip()}:{PORT}")
            print("等待客户端连接...")
            
            while self.running:
                try:
                    # 接受客户端连接
                    self.client_socket, addr = self.server_socket.accept()
                    print(f"客户端已连接: {addr[0]}:{addr[1]}")
                    
                    # 处理客户端请求
                    self.handle_client()
                    
                except Exception as e:
                    print(f"处理客户端连接时出错: {str(e)}")
                    if self.client_socket:
                        self.client_socket.close()
                    self.client_socket = None
                    
        except Exception as e:
            print(f"启动服务器时出错: {str(e)}")
        finally:
            self.stop_server()
    
    def handle_client(self):
        """处理客户端请求"""
        try:
            # 接收握手消息
            data = self.client_socket.recv(HEADER_SIZE)
            msg_len = struct.unpack('!I', data[:HEADER_SIZE])[0]
            msg_data = self.client_socket.recv(msg_len)
            message = ProtocolMessage.from_json(msg_data.decode('utf-8'))
            
            if message.msg_type != MSG_TYPE_HANDSHAKE:
                print(f"无效的握手消息: {message.msg_type}")
                return
            
            print(f"收到握手消息，客户端: {message.client_name}")
            
            # 发送握手响应
            response = HandshakeMessage(client_name="Test Receiver")
            self.client_socket.send(pack_message(response))
            
            # 处理文件传输
            self.receive_files()
            
        except Exception as e:
            print(f"处理客户端请求时出错: {str(e)}")
    
    def receive_files(self):
        """接收文件"""
        try:
            while True:
                # 接收消息头
                data = self.client_socket.recv(HEADER_SIZE)
                if not data:
                    break
                    
                # 解析消息长度
                msg_len = struct.unpack('!I', data[:HEADER_SIZE])[0]
                
                # 接收消息数据
                msg_data = b''
                remaining = msg_len
                while remaining > 0:
                    chunk = self.client_socket.recv(min(remaining, BUFFER_SIZE))
                    if not chunk:
                        break
                    msg_data += chunk
                    remaining -= len(chunk)
                
                # 解析消息
                try:
                    # 尝试解析JSON部分
                    json_part = msg_data.split(b'}', 1)[0] + b'}'
                    json_data = json.loads(json_part.decode('utf-8'))
                    msg_type = json_data.get('msg_type')
                    
                    if msg_type == MSG_TYPE_FILE_INFO:
                        # 文件信息消息
                        info_data = json.loads(msg_data.decode('utf-8'))
                        print(f"准备接收文件: {info_data['filename']} ({info_data['filesize']} 字节)")
                        print(f"文件进度: {info_data['current_file']}/{info_data['file_count']}")
                        
                        # 创建文件
                        self.current_file = os.path.join(self.save_dir, info_data['filename'])
                        self.current_file_size = info_data['filesize']
                        self.received_bytes = 0
                        self.file_handle = open(self.current_file, 'wb')
                        
                    elif msg_type == MSG_TYPE_FILE_DATA:
                        # 文件数据消息
                        file_data = msg_data[len(json_part):]
                        self.file_handle.write(file_data)
                        self.received_bytes += len(file_data)
                        
                        # 显示进度
                        progress = int((self.received_bytes / self.current_file_size) * 100)
                        print(f"\r接收进度: {progress}%", end="")
                        
                    elif msg_type == MSG_TYPE_FILE_END:
                        # 关闭文件
                        self.file_handle.close()
                        print(f"\n文件接收完成: {os.path.basename(self.current_file)}")
                        
                    elif msg_type == MSG_TYPE_BATCH_END:
                        print("所有文件接收完成")
                        break
                        
                except Exception as e:
                    print(f"解析消息时出错: {str(e)}")
                    break
                    
        except Exception as e:
            print(f"接收文件时出错: {str(e)}")
            if hasattr(self, 'file_handle'):
                self.file_handle.close()
    
    def stop_server(self):
        """停止服务器"""
        self.running = False
        
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            
        print("服务器已停止")

def main():
    """主函数"""
    receiver = CommandLineReceiver()
    
    try:
        receiver.start_server()
    except KeyboardInterrupt:
        print("\n收到中断信号，正在停止服务器...")
        receiver.stop_server()

if __name__ == "__main__":
    main()