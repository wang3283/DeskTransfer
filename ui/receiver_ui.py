"""
接收端用户界面
提供接收端的图形界面
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import os
import sys
import json
import socket
import struct
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import *
from common.utils import get_local_ip, find_available_port, format_size, create_received_dir

class ReceiverUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DeskTransfer - 接收端")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # 初始化变量
        self.server = None
        self.is_running = False
        self.current_received_dir = None
        self.received_files = []
        self.total_received = 0
        self.total_size = 0
        self.history_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "transfer_history.json")
        self.transfer_history = []
        
        # 加载传输历史记录
        self.load_transfer_history()
        
        # 创建界面
        self.create_widgets()
        
        # 设置拖拽功能
        self.setup_drag_drop()
        
        # 设置关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建笔记本控件，用于切换不同页面
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 服务器页面
        server_frame = ttk.Frame(notebook)
        notebook.add(server_frame, text="服务器")
        
        # 历史记录页面
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="传输历史")
        
        # 创建服务器页面内容
        self.create_server_tab(server_frame)
        
        # 创建历史记录页面内容
        self.create_history_tab(history_frame)
    
    def create_server_tab(self, parent):
        """创建服务器页面内容"""
        # 服务器信息框架
        info_frame = ttk.LabelFrame(parent, text="服务器信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # IP地址和端口显示
        ip_frame = ttk.Frame(info_frame)
        ip_frame.pack(fill=tk.X)
        
        self.ip_label = ttk.Label(ip_frame, text=f"IP地址: {get_local_ip()}")
        self.ip_label.pack(side=tk.LEFT)
        
        self.refresh_ip_button = ttk.Button(ip_frame, text="刷新IP", command=self.refresh_ip)
        self.refresh_ip_button.pack(side=tk.LEFT, padx=(5, 0))
        
        self.port_label = ttk.Label(info_frame, text=f"端口: {PORT}")
        self.port_label.pack(anchor=tk.W)
        
        self.status_label = ttk.Label(info_frame, text="状态: 未启动", foreground="red")
        self.status_label.pack(anchor=tk.W)
        
        # 控制按钮框架
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="启动服务器", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="停止服务器", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.open_folder_button = ttk.Button(control_frame, text="打开接收文件夹", command=self.open_received_folder)
        self.open_folder_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(control_frame, text="清空记录", command=self.clear_log)
        self.clear_button.pack(side=tk.RIGHT)
        
        # 接收信息框架
        receive_frame = ttk.LabelFrame(parent, text="接收信息", padding="10")
        receive_frame.pack(fill=tk.BOTH, expand=True)
        
        # 当前接收目录
        self.current_dir_label = ttk.Label(receive_frame, text="接收目录: 未设置")
        self.current_dir_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 统计信息
        stats_frame = ttk.Frame(receive_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.files_count_label = ttk.Label(stats_frame, text="已接收文件: 0")
        self.files_count_label.pack(side=tk.LEFT)
        
        self.total_size_label = ttk.Label(stats_frame, text="总大小: 0 B")
        self.total_size_label.pack(side=tk.RIGHT)
        
        # 进度条
        self.progress = ttk.Progressbar(receive_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_label = ttk.Label(receive_frame, text="等待传输...")
        self.progress_label.pack(anchor=tk.W)
        
        # 日志文本框
        log_frame = ttk.LabelFrame(parent, text="传输日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def create_history_tab(self, parent):
        """创建历史记录页面内容"""
        # 历史记录框架
        history_frame = ttk.LabelFrame(parent, text="传输历史", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # 按钮框架
        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_frame, text="刷新历史", command=self.refresh_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空历史", command=self.clear_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="导出历史", command=self.export_history).pack(side=tk.LEFT)
        
        # 历史记录列表
        list_frame = ttk.Frame(history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 历史记录树形视图
        self.history_tree = ttk.Treeview(list_frame, columns=("时间", "文件名", "大小", "类型"), show="headings", yscrollcommand=scrollbar.set)
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_tree.yview)
        
        # 设置列标题和宽度
        self.history_tree.heading("时间", text="传输时间")
        self.history_tree.heading("文件名", text="文件名")
        self.history_tree.heading("大小", text="大小")
        self.history_tree.heading("类型", text="类型")
        
        self.history_tree.column("时间", width=150)
        self.history_tree.column("文件名", width=250)
        self.history_tree.column("大小", width=100)
        self.history_tree.column("类型", width=80)
        
        # 绑定双击事件，用于打开文件
        self.history_tree.bind("<Double-1>", self.open_history_file)
        
        # 右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="打开文件", command=self.open_selected_file)
        self.context_menu.add_command(label="打开所在文件夹", command=self.open_file_location)
        self.history_tree.bind("<Button-3>", self.show_context_menu)
        
        # 初始加载历史记录
        self.refresh_history()
    
    def setup_drag_drop(self):
        """设置拖拽功能"""
        # 为整个窗口设置拖拽接收
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
    
    def on_drop(self, event):
        """处理拖拽事件，将文件保存到接收目录"""
        if not self.current_received_dir:
            messagebox.showwarning("警告", "请先启动服务器以设置接收目录")
            return
            
        files = self.root.tk.splitlist(event.data)
        saved_count = 0
        
        for file_path in files:
            # 移除文件路径前后的可能引号
            file_path = file_path.strip('"\'')
            
            # 检查是否是文件
            if os.path.isfile(file_path):
                try:
                    # 复制文件到接收目录
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(self.current_received_dir, filename)
                    
                    # 如果文件已存在，添加时间戳
                    if os.path.exists(dest_path):
                        name, ext = os.path.splitext(filename)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{name}_{timestamp}{ext}"
                        dest_path = os.path.join(self.current_received_dir, filename)
                    
                    # 复制文件
                    import shutil
                    shutil.copy2(file_path, dest_path)
                    
                    # 添加到历史记录
                    file_size = os.path.getsize(dest_path)
                    self.add_to_history(filename, file_size, "拖拽上传")
                    
                    saved_count += 1
                except Exception as e:
                    self.log_message(f"保存文件失败: {filename}, 错误: {str(e)}")
        
        if saved_count > 0:
            self.log_message(f"通过拖拽保存了 {saved_count} 个文件到接收目录")
            self.refresh_history()
    
    def load_transfer_history(self):
        """加载传输历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.transfer_history = json.load(f)
            else:
                self.transfer_history = []
        except Exception as e:
            self.log_message(f"加载历史记录失败: {str(e)}")
            self.transfer_history = []
    
    def save_transfer_history(self):
        """保存传输历史记录"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.transfer_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_message(f"保存历史记录失败: {str(e)}")
    
    def add_to_history(self, filename, filesize, transfer_type):
        """添加记录到历史"""
        record = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": filename,
            "filesize": filesize,
            "type": transfer_type,
            "path": os.path.join(self.current_received_dir, filename) if self.current_received_dir else ""
        }
        
        self.transfer_history.append(record)
        self.save_transfer_history()
    
    def refresh_history(self):
        """刷新历史记录显示"""
        # 清空当前显示
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # 按时间倒序显示历史记录
        for record in reversed(self.transfer_history):
            self.history_tree.insert("", "end", values=(
                record["time"],
                record["filename"],
                format_size(record["filesize"]),
                record["type"]
            ))
    
    def clear_history(self):
        """清空历史记录"""
        if messagebox.askyesno("确认", "确定要清空所有历史记录吗？"):
            self.transfer_history = []
            self.save_transfer_history()
            self.refresh_history()
            self.log_message("已清空历史记录")
    
    def export_history(self):
        """导出历史记录"""
        file_path = filedialog.asksaveasfilename(
            title="导出历史记录",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("传输时间\t文件名\t大小\t类型\n")
                    for record in self.transfer_history:
                        f.write(f"{record['time']}\t{record['filename']}\t{format_size(record['filesize'])}\t{record['type']}\n")
                
                messagebox.showinfo("成功", f"历史记录已导出到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def open_history_file(self, event):
        """双击打开历史记录中的文件"""
        self.open_selected_file()
    
    def open_selected_file(self):
        """打开选中的文件"""
        selection = self.history_tree.selection()
        if not selection:
            return
            
        # 获取选中的记录
        item = self.history_tree.item(selection[0])
        filename = item["values"][1]
        
        # 在历史记录中查找完整路径
        for record in self.transfer_history:
            if record["filename"] == filename and record["path"]:
                file_path = record["path"]
                if os.path.exists(file_path):
                    self.open_file_with_default_app(file_path)
                    return
                else:
                    messagebox.showwarning("警告", f"文件不存在: {file_path}")
                    return
        
        messagebox.showwarning("警告", f"未找到文件: {filename}")
    
    def open_file_location(self):
        """打开文件所在位置"""
        selection = self.history_tree.selection()
        if not selection:
            return
            
        # 获取选中的记录
        item = self.history_tree.item(selection[0])
        filename = item["values"][1]
        
        # 在历史记录中查找完整路径
        for record in self.transfer_history:
            if record["filename"] == filename and record["path"]:
                file_path = record["path"]
                if os.path.exists(file_path):
                    self.open_file_location_with_default_app(file_path)
                    return
                else:
                    messagebox.showwarning("警告", f"文件不存在: {file_path}")
                    return
        
        messagebox.showwarning("警告", f"未找到文件: {filename}")
    
    def open_file_with_default_app(self, file_path):
        """使用默认应用程序打开文件"""
        import subprocess
        import platform
        
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", file_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {str(e)}")
    
    def open_file_location_with_default_app(self, file_path):
        """打开文件所在位置"""
        import subprocess
        import platform
        
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["explorer", "/select,", file_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", "-R", file_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", os.path.dirname(file_path)])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件位置: {str(e)}")
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 选中右键点击的项目
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def log_message(self, message):
        """在日志文本框中添加消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def start_server(self):
        """启动服务器"""
        if self.is_running:
            return
        
        # 创建接收目录
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "received")
        self.current_received_dir = create_received_dir(data_dir)
        self.current_dir_label.config(text=f"接收目录: {self.current_received_dir}")
        
        # 启动服务器线程
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # 更新UI状态
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="状态: 运行中", foreground="green")
        
        self.log_message(f"服务器已启动，监听端口 {PORT}")
        self.log_message(f"接收目录: {self.current_received_dir}")
    
    def stop_server(self):
        """停止服务器"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 关闭服务器
        if self.server:
            self.server.close()
        
        # 更新UI状态
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="状态: 已停止", foreground="red")
        
        self.log_message("服务器已停止")
    
    def run_server(self):
        """运行服务器"""
        try:
            import socket
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(('', PORT))
            self.server.listen(5)
            
            while self.is_running:
                try:
                    # 设置超时，以便可以检查is_running标志
                    self.server.settimeout(1.0)
                    client_socket, addr = self.server.accept()
                    
                    # 处理客户端连接
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.is_running:
                        self.log_message(f"服务器错误: {str(e)}")
                    break
                    
        except Exception as e:
            self.log_message(f"无法启动服务器: {str(e)}")
            self.stop_server()
    
    def handle_client(self, client_socket, addr):
        """处理客户端连接"""
        try:
            self.log_message(f"客户端连接: {addr[0]}:{addr[1]}")
            
            # 接收握手消息
            data = client_socket.recv(HEADER_SIZE)
            if not data:
                return
                
            msg_len = struct.unpack('!I', data[:HEADER_SIZE])[0]
            msg_data = client_socket.recv(msg_len)
            handshake = ProtocolMessage.from_json(msg_data.decode('utf-8'))
            
            if handshake.msg_type != MSG_TYPE_HANDSHAKE:
                self.log_message(f"无效的握手消息: {handshake.msg_type}")
                return
                
            self.log_message(f"握手成功，客户端: {handshake.client_name}")
            
            # 发送握手响应
            response = HandshakeMessage(client_name="DeskTransfer Receiver")
            client_socket.send(pack_message(response))
            
            # 处理文件传输
            self.receive_files(client_socket)
            
        except Exception as e:
            self.log_message(f"处理客户端连接时出错: {str(e)}")
        finally:
            client_socket.close()
            self.log_message(f"客户端断开连接: {addr[0]}:{addr[1]}")
    
    def receive_files(self, client_socket):
        """接收文件"""
        current_file = None
        current_file_size = 0
        received_size = 0
        file_count = 0
        current_file_num = 0
        
        while self.is_running:
            try:
                # 接收消息头
                header = client_socket.recv(HEADER_SIZE)
                if not header:
                    break
                    
                msg_len = struct.unpack('!I', header[:HEADER_SIZE])[0]
                msg_data = client_socket.recv(msg_len)
                message = ProtocolMessage.from_json(msg_data.decode('utf-8'))
                
                if message.msg_type == MSG_TYPE_FILE_INFO:
                    # 文件信息消息
                    file_info = message
                    current_file = file_info.filename
                    current_file_size = file_info.filesize
                    file_count = file_info.file_count
                    current_file_num = file_info.current_file
                    received_size = 0
                    
                    self.root.after(0, self.update_progress, 0, 
                                   f"接收文件 {current_file_num}/{file_count}: {current_file}")
                    
                elif message.msg_type == MSG_TYPE_FILE_DATA:
                    # 文件数据消息
                    file_data = message
                    file_path = os.path.join(self.current_received_dir, current_file)
                    
                    with open(file_path, 'ab') as f:
                        f.write(file_data.data)
                    
                    received_size += len(file_data.data)
                    progress = int((received_size / current_file_size) * 100) if current_file_size > 0 else 0
                    
                    self.root.after(0, self.update_progress, progress, 
                                   f"接收文件 {current_file_num}/{file_count}: {current_file} ({format_size(received_size)}/{format_size(current_file_size)})")
                    
                elif message.msg_type == MSG_TYPE_FILE_END:
                    # 文件传输结束
                    file_path = os.path.join(self.current_received_dir, current_file)
                    self.received_files.append(file_path)
                    self.total_received += 1
                    self.total_size += current_file_size
                    
                    # 添加到历史记录
                    self.add_to_history(current_file, current_file_size, "网络接收")
                    
                    self.root.after(0, self.update_stats)
                    self.log_message(f"文件接收完成: {current_file} ({format_size(current_file_size)})")
                    
                elif message.msg_type == MSG_TYPE_BATCH_END:
                    # 批量传输结束
                    self.log_message(f"批量传输完成，共接收 {file_count} 个文件")
                    self.root.after(0, self.update_progress, 100, "传输完成")
                    
                elif message.msg_type == MSG_TYPE_ERROR:
                    # 错误消息
                    error = message
                    self.log_message(f"传输错误: {error.error_msg}")
                    
            except Exception as e:
                self.log_message(f"接收文件时出错: {str(e)}")
                break
    
    def update_progress(self, value, text):
        """更新进度条"""
        self.progress['value'] = value
        self.progress_label.config(text=text)
    
    def update_stats(self):
        """更新统计信息"""
        self.files_count_label.config(text=f"已接收文件: {self.total_received}")
        self.total_size_label.config(text=f"总大小: {format_size(self.total_size)}")
    
    def open_received_folder(self):
        """打开接收文件夹"""
        if self.current_received_dir and os.path.exists(self.current_received_dir):
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                os.startfile(self.current_received_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", self.current_received_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", self.current_received_dir])
        else:
            messagebox.showinfo("提示", "接收文件夹不存在或未设置")
    
    def refresh_ip(self):
        """刷新IP地址显示"""
        try:
            # 获取所有可用的IP地址
            available_ips = self.get_available_ips()
            
            if available_ips:
                # 显示所有IP地址，第一个是主IP
                primary_ip = available_ips[0]
                if len(available_ips) == 1:
                    self.ip_label.config(text=f"IP地址: {primary_ip}")
                else:
                    self.ip_label.config(text=f"IP地址: {primary_ip} (+{len(available_ips)-1}个)")
                
                self.log_message(f"已刷新IP地址: {', '.join(available_ips)}")
            else:
                self.ip_label.config(text="IP地址: 未找到")
                self.log_message("未找到可用的IP地址")
                
        except Exception as e:
            self.log_message(f"刷新IP地址失败: {str(e)}")
    
    def get_available_ips(self):
        """获取所有可用的IP地址"""
        try:
            import psutil
            
            # 获取所有网络接口
            ips = []
            
            # 添加常用局域网IP段
            common_ips = ["192.168.1.1", "192.168.0.1", "10.0.0.1", "172.16.0.1"]
            
            # 获取所有网络接口的IP地址
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        ip = addr.address
                        if not ip.startswith('127.') and ip not in common_ips:
                            ips.append(f"{ip} ({interface})")
            
            # 添加常用局域网IP段
            for ip in common_ips:
                ips.append(ip)
            
            # 如果没有找到任何IP，使用get_local_ip作为后备
            if not ips:
                fallback_ip = get_local_ip()
                if fallback_ip and fallback_ip != "127.0.0.1":
                    ips.append(fallback_ip)
            
            return ips
            
        except Exception as e:
            # 如果psutil不可用，使用原始方法
            try:
                import socket
                fallback_ip = get_local_ip()
                if fallback_ip and fallback_ip != "127.0.0.1":
                    return [fallback_ip]
                return []
            except:
                return []

    def clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def on_closing(self):
        """窗口关闭事件处理"""
        if self.is_running:
            if messagebox.askokcancel("退出", "服务器正在运行，确定要退出吗？"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """主函数"""
    root = TkinterDnD.Tk()
    app = ReceiverUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()