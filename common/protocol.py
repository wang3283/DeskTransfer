"""
通信协议定义
定义发送端和接收端之间的通信协议
"""
import json
import struct
import os

# 协议常量
HEADER_SIZE = 4  # 消息头大小（字节）
BUFFER_SIZE = 4096  # 缓冲区大小
PORT = 12345  # 默认端口

# 消息类型
MSG_TYPE_HANDSHAKE = "handshake"  # 握手消息
MSG_TYPE_FILE_INFO = "file_info"  # 文件信息消息
MSG_TYPE_FILE_DATA = "file_data"  # 文件数据消息
MSG_TYPE_FILE_END = "file_end"  # 文件传输结束消息
MSG_TYPE_BATCH_END = "batch_end"  # 批量传输结束消息
MSG_TYPE_ERROR = "error"  # 错误消息

# 支持的图片格式
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

class ProtocolMessage:
    """协议消息基类"""
    def __init__(self, msg_type):
        self.msg_type = msg_type
    
    def to_json(self):
        """将消息转换为JSON字符串"""
        return json.dumps({
            'msg_type': self.msg_type,
            **self.__dict__
        })
    
    @classmethod
    def from_json(cls, json_str):
        """从JSON字符串创建消息对象"""
        data = json.loads(json_str)
        msg_type = data.pop('msg_type')
        
        if msg_type == MSG_TYPE_HANDSHAKE:
            return HandshakeMessage(**data)
        elif msg_type == MSG_TYPE_FILE_INFO:
            return FileInfoMessage(**data)
        elif msg_type == MSG_TYPE_FILE_DATA:
            return FileDataMessage(**data)
        elif msg_type == MSG_TYPE_FILE_END:
            return FileEndMessage(**data)
        elif msg_type == MSG_TYPE_BATCH_END:
            return BatchEndMessage(**data)
        elif msg_type == MSG_TYPE_ERROR:
            return ErrorMessage(**data)
        else:
            raise ValueError(f"未知的消息类型: {msg_type}")

class HandshakeMessage(ProtocolMessage):
    """握手消息"""
    def __init__(self, client_name="DeskTransfer Sender"):
        super().__init__(MSG_TYPE_HANDSHAKE)
        self.client_name = client_name

class FileInfoMessage(ProtocolMessage):
    """文件信息消息"""
    def __init__(self, filename, filesize, file_count=1, current_file=1):
        super().__init__(MSG_TYPE_FILE_INFO)
        self.filename = os.path.basename(filename)
        self.filesize = filesize
        self.file_count = file_count
        self.current_file = current_file

class FileDataMessage(ProtocolMessage):
    """文件数据消息"""
    def __init__(self, data):
        super().__init__(MSG_TYPE_FILE_DATA)
        self.data = data

class FileEndMessage(ProtocolMessage):
    """文件传输结束消息"""
    def __init__(self):
        super().__init__(MSG_TYPE_FILE_END)

class BatchEndMessage(ProtocolMessage):
    """批量传输结束消息"""
    def __init__(self):
        super().__init__(MSG_TYPE_BATCH_END)

class ErrorMessage(ProtocolMessage):
    """错误消息"""
    def __init__(self, error_msg):
        super().__init__(MSG_TYPE_ERROR)
        self.error_msg = error_msg

def pack_message(msg):
    """打包消息，添加消息头"""
    if msg.msg_type == MSG_TYPE_FILE_DATA:
        # 文件数据消息特殊处理
        msg_bytes = json.dumps({
            'msg_type': msg.msg_type
        }).encode('utf-8')
        msg_len = len(msg_bytes) + len(msg.data)
        header = struct.pack('!I', msg_len)  # 使用网络字节序打包消息长度
        return header + msg_bytes + msg.data
    else:
        # 其他消息正常处理
        msg_bytes = msg.to_json().encode('utf-8')
        msg_len = len(msg_bytes)
        header = struct.pack('!I', msg_len)  # 使用网络字节序打包消息长度
        return header + msg_bytes

def unpack_message(data):
    """解包消息，解析消息头"""
    msg_len = struct.unpack('!I', data[:HEADER_SIZE])[0]
    msg_data = data[HEADER_SIZE:HEADER_SIZE+msg_len]
    
    # 检查是否是文件数据消息
    try:
        # 尝试解析JSON
        json_data = json.loads(msg_data.decode('utf-8'))
        msg_type = json_data.get('msg_type')
        
        if msg_type == MSG_TYPE_FILE_DATA:
            # 文件数据消息，数据在JSON之后
            file_data = data[HEADER_SIZE+len(msg_data):]
            return FileDataMessage(data=file_data)
        else:
            # 其他消息，正常解析
            return ProtocolMessage.from_json(msg_data.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        # 如果JSON解析失败，可能是文件数据消息
        # 尝试从消息开头获取消息类型
        try:
            json_part = msg_data.split(b'}', 1)[0] + b'}'
            json_data = json.loads(json_part.decode('utf-8'))
            if json_data.get('msg_type') == MSG_TYPE_FILE_DATA:
                # 文件数据消息，数据在JSON之后
                file_data = data[HEADER_SIZE+len(json_part):]
                return FileDataMessage(data=file_data)
        except:
            pass
        
        # 如果都失败，抛出异常
        raise ValueError("无法解析消息")

def is_image_file(filename):
    """检查文件是否为支持的图片格式"""
    _, ext = os.path.splitext(filename.lower())
    return ext in SUPPORTED_IMAGE_FORMATS