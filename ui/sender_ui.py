"""
发送端用户界面
提供发送端的图形界面
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import os
import sys
import struct
import json
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import *
from common.utils import get_local_ip, validate_ip_address, format_size
from common.protocol import is_image_file

class SenderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DeskTransfer - 发送端")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # 初始化变量
        self.selected_files = []
        self.is_sending = False
        self.client_socket = None
        
        # 历史记录相关
        self.history_file = os.path.join(os.path.expanduser("~"), ".desktransfer", "sender_history.json")
        self.transfer_history = []
        
        # 创建界面
        self.create_widgets()
        
        # 设置拖拽功能
        self.setup_drag_drop()
        
        # 加载历史记录
        self.load_transfer_history()
        
        # 设置关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建笔记本控件（标签页）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建发送标签页
        self.send_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.send_frame, text="发送")
        
        # 创建历史记录标签页
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="传输历史")
        
        # 在发送标签页中创建原有组件
        self.create_send_tab()
        
        # 在历史记录标签页中创建历史记录组件
        self.create_history_tab()
    
    def create_send_tab(self):
        """创建发送标签页的内容"""
        # 连接设置框架
        connection_frame = ttk.LabelFrame(self.send_frame, text="连接设置", padding="10")
        connection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # IP地址输入
        ip_frame = ttk.Frame(connection_frame)
        ip_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(ip_frame, text="接收端IP地址:").pack(side=tk.LEFT)
        
        # 创建IP地址下拉菜单
        self.ip_var = tk.StringVar(value="")
        self.ip_combo = ttk.Combobox(ip_frame, textvariable=self.ip_var, width=20, state="readonly")
        self.ip_combo.pack(side=tk.LEFT, padx=(5, 5))
        
        # 获取并设置所有可用的IP地址
        self.available_ips = self.get_available_ips()
        self.ip_combo['values'] = self.available_ips
        
        # 如果有可用IP，默认选择第一个
        if self.available_ips:
            self.ip_combo.current(0)
        
        # 刷新IP地址按钮
        self.refresh_ip_button = ttk.Button(ip_frame, text="刷新IP", command=self.refresh_available_ips)
        self.refresh_ip_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 端口显示
        port_frame = ttk.Frame(connection_frame)
        port_frame.pack(fill=tk.X)
        
        ttk.Label(port_frame, text="端口:").pack(side=tk.LEFT)
        self.port_label = ttk.Label(port_frame, text=str(PORT))
        self.port_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 文件选择框架
        file_frame = ttk.LabelFrame(self.send_frame, text="文件选择", padding="10")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 文件列表
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 文件列表框
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, 
                                       yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # 文件操作按钮
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X)
        
        self.add_button = ttk.Button(button_frame, text="添加文件", command=self.add_files)
        self.add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.remove_button = ttk.Button(button_frame, text="移除选中", command=self.remove_selected)
        self.remove_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(button_frame, text="清空列表", command=self.clear_list)
        self.clear_button.pack(side=tk.LEFT)
        
        # 文件信息
        self.file_info_label = ttk.Label(file_frame, text="已选择 0 个文件，总大小: 0 B")
        self.file_info_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 传输控制框架
        control_frame = ttk.LabelFrame(self.send_frame, text="传输控制", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 连接和发送按钮
        button_frame2 = ttk.Frame(control_frame)
        button_frame2.pack(fill=tk.X)
        
        self.connect_button = ttk.Button(button_frame2, text="连接", command=self.connect_to_receiver)
        self.connect_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.send_button = ttk.Button(button_frame2, text="发送文件", command=self.send_files, state=tk.DISABLED)
        self.send_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.disconnect_button = ttk.Button(button_frame2, text="断开连接", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_button.pack(side=tk.LEFT)
        
        # 连接状态
        self.status_label = ttk.Label(control_frame, text="状态: 未连接", foreground="red")
        self.status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 进度条
        self.progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(5, 0))
        
        self.progress_label = ttk.Label(control_frame, text="等待传输...")
        self.progress_label.pack(anchor=tk.W)
        
        # 日志框架
        log_frame = ttk.LabelFrame(self.send_frame, text="传输日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def create_history_tab(self):
        """创建历史记录标签页的内容"""
        # 工具栏
        toolbar_frame = ttk.Frame(self.history_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="刷新", command=self.refresh_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="清空记录", command=self.clear_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="导出记录", command=self.export_history).pack(side=tk.LEFT)
        
        # 历史记录表格
        history_frame = ttk.Frame(self.history_frame)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        columns = ("时间", "文件名", "大小", "接收端", "状态")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.history_tree.bind("<Double-1>", self.open_history_file)
        
        # 创建右键菜单
        self.context_menu = tk.Menu(self.history_tree, tearoff=0)
        self.context_menu.add_command(label="打开文件", command=self.open_selected_file)
        self.context_menu.add_command(label="打开文件位置", command=self.open_file_location)
        
        # 绑定右键菜单
        self.history_tree.bind("<Button-3>", self.show_context_menu)
    
    def setup_drag_drop(self):
        """设置拖拽功能"""
        # 为文件列表框设置拖拽接收
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.on_drop)
        
        # 为整个窗口设置拖拽接收
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop_window)
    
    def on_drop(self, event):
        """处理文件列表框的拖拽事件"""
        files = self.root.tk.splitlist(event.data)
        self.add_dropped_files(files)
    
    def on_drop_window(self, event):
        """处理窗口的拖拽事件"""
        files = self.root.tk.splitlist(event.data)
        self.add_dropped_files(files)
    
    def add_dropped_files(self, file_paths):
        """添加拖拽的文件"""
        added_count = 0
        for file_path in file_paths:
            # 移除文件路径前后的可能引号
            file_path = file_path.strip('"\'')
            
            # 检查是否是文件
            if os.path.isfile(file_path) and is_image_file(file_path) and file_path not in self.selected_files:
                self.selected_files.append(file_path)
                filename = os.path.basename(file_path)
                self.file_listbox.insert(tk.END, filename)
                added_count += 1
        
        if added_count > 0:
            self.update_file_info()
            self.log_message(f"通过拖拽添加了 {added_count} 个文件")
    
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
    
    def add_to_history(self, filename, filesize, receiver_ip, status):
        """添加记录到历史"""
        record = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": filename,
            "filesize": filesize,
            "receiver": receiver_ip,
            "status": status,
            "path": filename  # 发送端记录原始文件路径
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
                record["receiver"],
                record["status"]
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
                    f.write("传输时间\t文件名\t大小\t接收端\t状态\n")
                    for record in self.transfer_history:
                        f.write(f"{record['time']}\t{record['filename']}\t{format_size(record['filesize'])}\t{record['receiver']}\t{record['status']}\n")
                
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
    
    def add_files(self):
        """添加文件到列表"""
        file_paths = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_paths:
            for file_path in file_paths:
                if is_image_file(file_path) and file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    # 只显示文件名，不显示完整路径
                    filename = os.path.basename(file_path)
                    self.file_listbox.insert(tk.END, filename)
            
            self.update_file_info()
            self.log_message(f"添加了 {len(file_paths)} 个文件")
    
    def remove_selected(self):
        """移除选中的文件"""
        selected_indices = self.file_listbox.curselection()
        
        # 从后往前删除，避免索引变化
        for index in reversed(selected_indices):
            self.file_listbox.delete(index)
            del self.selected_files[index]
        
        self.update_file_info()
    
    def clear_list(self):
        """清空文件列表"""
        self.file_listbox.delete(0, tk.END)
        self.selected_files.clear()
        self.update_file_info()
    
    def update_file_info(self):
        """更新文件信息显示"""
        file_count = len(self.selected_files)
        total_size = sum(os.path.getsize(file_path) for file_path in self.selected_files)
        
        self.file_info_label.config(
            text=f"已选择 {file_count} 个文件，总大小: {format_size(total_size)}"
        )
    
    def connect_to_receiver(self):
        """连接到接收端"""
        ip_entry = self.ip_var.get().strip()
        
        # 如果下拉菜单中的值包含接口名（如 "192.168.1.100 (en0)"），则提取IP部分
        if '(' in ip_entry and ')' in ip_entry:
            ip_address = ip_entry.split('(')[0].strip()
        else:
            ip_address = ip_entry
        
        if not ip_address:
            messagebox.showerror("错误", "请输入接收端IP地址")
            return
        
        if not validate_ip_address(ip_address):
            messagebox.showerror("错误", "IP地址格式不正确")
            return
        
        if not self.selected_files:
            messagebox.showerror("错误", "请先选择要发送的文件")
            return
        
        # 启动连接线程
        self.connect_thread = threading.Thread(
            target=self.connect_worker,
            args=(ip_address,)
        )
        self.connect_thread.daemon = True
        self.connect_thread.start()
        
        # 更新UI状态
        self.connect_button.config(state=tk.DISABLED)
        self.status_label.config(text="状态: 正在连接...", foreground="orange")
        self.log_message(f"正在连接到 {ip_address}:{PORT}...")
    
    def connect_worker(self, ip_address):
        """连接工作线程"""
        try:
            import socket
            
            # 创建socket连接
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip_address, PORT))
            
            # 发送握手消息
            handshake = HandshakeMessage(client_name="DeskTransfer Sender")
            self.client_socket.send(pack_message(handshake))
            
            # 接收握手响应
            data = self.client_socket.recv(HEADER_SIZE)
            if not data:
                raise Exception("未收到响应")
                
            msg_len = struct.unpack('!I', data[:HEADER_SIZE])[0]
            msg_data = self.client_socket.recv(msg_len)
            response = ProtocolMessage.from_json(msg_data.decode('utf-8'))
            
            if response.msg_type != MSG_TYPE_HANDSHAKE:
                raise Exception(f"无效的握手响应: {response.msg_type}")
            
            # 连接成功
            self.root.after(0, self.on_connect_success, ip_address, response.client_name)
            
        except Exception as e:
            self.root.after(0, self.on_connect_error, str(e))
    
    def on_connect_success(self, ip_address, client_name):
        """连接成功回调"""
        self.status_label.config(text=f"状态: 已连接到 {client_name}", foreground="green")
        self.connect_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.NORMAL)
        self.log_message(f"成功连接到 {ip_address}:{PORT} ({client_name})")
    
    def on_connect_error(self, error_msg):
        """连接错误回调"""
        self.status_label.config(text="状态: 连接失败", foreground="red")
        self.connect_button.config(state=tk.NORMAL)
        self.log_message(f"连接失败: {error_msg}")
        messagebox.showerror("连接失败", error_msg)
        
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
    
    def disconnect(self):
        """断开连接"""
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        
        self.status_label.config(text="状态: 未连接", foreground="red")
        self.connect_button.config(state=tk.NORMAL)
        self.send_button.config(state=tk.DISABLED)
        self.disconnect_button.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.progress_label.config(text="等待传输...")
        
        self.log_message("已断开连接")
    
    def send_files(self):
        """发送文件"""
        if not self.selected_files:
            messagebox.showerror("错误", "请先选择要发送的文件")
            return
        
        if not self.client_socket:
            messagebox.showerror("错误", "未连接到接收端")
            return
        
        # 启动发送线程
        self.send_thread = threading.Thread(target=self.send_worker)
        self.send_thread.daemon = True
        self.send_thread.start()
        
        # 更新UI状态
        self.is_sending = True
        self.send_button.config(state=tk.DISABLED)
        self.disconnect_button.config(state=tk.DISABLED)
        self.status_label.config(text="状态: 正在发送...", foreground="blue")
    
    def send_worker(self):
        """发送工作线程"""
        try:
            file_count = len(self.selected_files)
            receiver_ip = self.ip_var.get()
            
            for i, file_path in enumerate(self.selected_files):
                if not self.is_sending:
                    break
                
                filename = os.path.basename(file_path)
                filesize = os.path.getsize(file_path)
                
                try:
                    # 发送文件信息
                    file_info = FileInfoMessage(
                        filename=filename,
                        filesize=filesize,
                        file_count=file_count,
                        current_file=i+1
                    )
                    self.client_socket.send(pack_message(file_info))
                    
                    # 更新进度
                    self.root.after(0, self.update_progress, 0, 
                                   f"发送文件 {i+1}/{file_count}: {filename}")
                    
                    # 发送文件数据
                    with open(file_path, 'rb') as f:
                        sent_bytes = 0
                        chunk_size = BUFFER_SIZE
                        
                        while sent_bytes < filesize and self.is_sending:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            
                            file_data = FileDataMessage(data=chunk)
                            self.client_socket.send(pack_message(file_data))
                            
                            sent_bytes += len(chunk)
                            progress = int((sent_bytes / filesize) * 100)
                            
                            self.root.after(0, self.update_progress, progress,
                                           f"发送文件 {i+1}/{file_count}: {filename} ({format_size(sent_bytes)}/{format_size(filesize)})")
                    
                    # 发送文件结束消息
                    file_end = FileEndMessage()
                    self.client_socket.send(pack_message(file_end))
                    
                    self.root.after(0, self.log_message, f"文件发送完成: {filename}")
                    # 添加成功记录到历史
                    self.root.after(0, lambda fn=filename, fs=filesize: self.add_to_history(fn, fs, receiver_ip, "发送成功"))
                    
                except Exception as file_error:
                    self.root.after(0, self.log_message, f"文件发送失败: {filename} - {str(file_error)}")
                    # 添加失败记录到历史
                    self.root.after(0, lambda fn=filename, fs=filesize: self.add_to_history(fn, fs, receiver_ip, "发送失败"))
            
            # 刷新历史记录显示
            self.root.after(0, self.refresh_history)
            
            # 发送批量传输结束消息
            if self.is_sending:
                batch_end = BatchEndMessage()
                self.client_socket.send(pack_message(batch_end))
                
                self.root.after(0, self.on_send_complete)
            
        except Exception as e:
            self.root.after(0, self.on_send_error, str(e))
    
    def update_progress(self, value, text):
        """更新进度条"""
        self.progress['value'] = value
        self.progress_label.config(text=text)
    
    def on_send_complete(self):
        """发送完成回调"""
        self.is_sending = False
        self.status_label.config(text="状态: 发送完成", foreground="green")
        self.send_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.NORMAL)
        self.progress['value'] = 100
        self.progress_label.config(text="传输完成")
        
        self.log_message("所有文件发送完成")
        messagebox.showinfo("传输完成", "所有文件已成功发送")
    
    def on_send_error(self, error_msg):
        """发送错误回调"""
        self.is_sending = False
        self.status_label.config(text="状态: 发送失败", foreground="red")
        self.send_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.NORMAL)
        
        self.log_message(f"发送失败: {error_msg}")
        messagebox.showerror("发送失败", error_msg)
    
    def get_available_ips(self):
        """获取所有可用的IP地址"""
        import socket
        import psutil
        
        ips = []
        
        try:
            # 获取所有网络接口
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    # 只获取IPv4地址，排除回环地址
                    if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                        ips.append(f"{addr.address} ({interface})")
            
            # 如果没有获取到IP，使用备用方法
            if not ips:
                local_ip = get_local_ip()
                if local_ip and local_ip != "127.0.0.1":
                    ips.append(local_ip)
            
            # 添加常用局域网IP段
            common_ips = [
                "192.168.1.100",
                "192.168.0.100",
                "10.0.0.100",
                "172.16.0.100"
            ]
            
            for ip in common_ips:
                if ip not in [x.split(' ')[0] for x in ips]:
                    ips.append(ip)
            
        except Exception as e:
            # 如果出错，至少返回本地IP
            local_ip = get_local_ip()
            if local_ip:
                ips.append(local_ip)
        
        return sorted(ips, key=lambda x: x.split(' ')[0])
    
    def refresh_available_ips(self):
        """刷新可用IP地址列表"""
        self.available_ips = self.get_available_ips()
        self.ip_combo['values'] = self.available_ips
        
        # 保持当前选择的IP（如果仍然可用）
        current_ip = self.ip_var.get().split(' ')[0]  # 只取IP部分，忽略接口名
        found = False
        
        for i, ip_with_interface in enumerate(self.available_ips):
            ip = ip_with_interface.split(' ')[0]
            if ip == current_ip:
                self.ip_combo.current(i)
                found = True
                break
        
        # 如果当前IP不在列表中，选择第一个
        if not found and self.available_ips:
            self.ip_combo.current(0)
        
        self.log_message(f"已刷新IP地址列表，共找到 {len(self.available_ips)} 个可用地址")
    
    def auto_fill_local_ip(self):
        """自动填充本地IP地址到接收端IP输入框"""
        local_ip = get_local_ip()
        
        # 查找包含本地IP的选项
        for i, ip_with_interface in enumerate(self.available_ips):
            ip = ip_with_interface.split(' ')[0]
            if ip == local_ip:
                self.ip_combo.current(i)
                self.log_message(f"已自动填充本地IP地址: {ip_with_interface}")
                return
        
        # 如果没找到，直接设置IP值
        self.ip_var.set(local_ip)
        self.log_message(f"已自动填充本地IP地址: {local_ip}")
    
    def on_closing(self):
        """窗口关闭事件处理"""
        if self.is_sending:
            if messagebox.askokcancel("退出", "正在传输文件，确定要退出吗？"):
                self.is_sending = False
                if self.client_socket:
                    self.client_socket.close()
                self.root.destroy()
        elif self.client_socket:
            if messagebox.askokcancel("退出", "已连接到接收端，确定要退出吗？"):
                if self.client_socket:
                    self.client_socket.close()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = TkinterDnD.Tk()
    app = SenderUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()