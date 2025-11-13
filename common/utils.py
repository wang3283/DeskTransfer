"""
工具函数
提供通用的辅助函数
"""
import os
import platform
import socket
import hashlib
from datetime import datetime

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 创建一个socket连接到公共DNS服务器
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 不需要实际连接，只是获取系统用于连接的IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_file_size(file_path):
    """获取文件大小（字节）"""
    return os.path.getsize(file_path)

def generate_file_id(file_path):
    """为文件生成唯一ID"""
    file_stat = os.stat(file_path)
    # 使用文件路径、大小和修改时间生成唯一ID
    unique_str = f"{file_path}_{file_stat.st_size}_{file_stat.st_mtime}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def format_size(size_bytes):
    """格式化文件大小显示"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"

def get_timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def create_received_dir(base_dir):
    """创建接收文件的目录，以时间戳命名"""
    timestamp = get_timestamp()
    received_dir = os.path.join(base_dir, timestamp)
    os.makedirs(received_dir, exist_ok=True)
    return received_dir

def validate_ip_address(ip):
    """验证IP地址格式"""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def get_system_info():
    """获取系统信息"""
    return {
        'os': platform.system(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor()
    }

def is_port_available(port):
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return True
    except OSError:
        return False

def find_available_port(start_port=12345, max_attempts=10):
    """查找可用端口"""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(port):
            return port
    return None