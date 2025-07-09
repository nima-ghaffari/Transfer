import os
import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import io
import ssl
import subprocess
import sys

FONT_FAMILY = "Berlin Sans FB Demi"
FONT_NORMAL = (FONT_FAMILY, 10)
FONT_BOLD = (FONT_FAMILY, 11, "bold")
FONT_MONO = ("Consolas", 11)

COLOR_BACKGROUND = "#000F08"
COLOR_FRAME_BORDER = "#3E2F5B"
COLOR_FRAME_BG = "#071410"
COLOR_WIDGET_BG = "#0E1F18"
COLOR_TEXT = "#F0F0F0"
COLOR_ACCENT = "#136F63"
COLOR_ACCENT_ACTIVE = "#1AAE95"
COLOR_ACCENT_TEXT = "#FFFFFF"
COLOR_SUCCESS = "#136F63"
COLOR_SUCCESS_TEXT = "#FFFFFF"
COLOR_ERROR = "#E74C3C"

class ClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Client")
        self.geometry("800x650")
        self.minsize(700, 600)
        self.configure(bg=COLOR_BACKGROUND)

        self.setup_styles()

        self.client_socket = None
        self.chat_socket = None
        self.chat_window = None
        self.is_connected = False
        self.checkbuttons = {}
        self.full_file_list = []
        self.ip_var = tk.StringVar()

        self.save_directory_var = tk.StringVar(value="Please select a base save folder...")
        self.use_new_folder_var = tk.BooleanVar(value=False)
        self.specific_download_path = None
        self.select_all_var = tk.BooleanVar(value=False)
        self.last_download_info = None

        self.create_widgets()
        self.update_exit_button_style()
        self.protocol("WM_DELETE_WINDOW", self.handle_exit_button)


    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('.', background=COLOR_BACKGROUND, foreground=COLOR_TEXT, fieldbackground=COLOR_WIDGET_BG, font=FONT_NORMAL, bordercolor=COLOR_FRAME_BORDER)
        style.configure('TLabel', background=COLOR_FRAME_BG)
        style.configure('TFrame', background=COLOR_BACKGROUND)
        style.configure('TLabelFrame', background=COLOR_FRAME_BG, relief="solid", borderwidth=1)
        style.configure('TLabelFrame.Label', foreground=COLOR_TEXT, background=COLOR_FRAME_BG, font=FONT_BOLD)
        style.configure('TCheckbutton', background=COLOR_FRAME_BG)
        style.map('TCheckbutton', indicatorbackground=[('active', COLOR_WIDGET_BG)], background=[('active', COLOR_FRAME_BG)])
        style.configure('TButton', background=COLOR_ACCENT, foreground=COLOR_ACCENT_TEXT, font=FONT_BOLD, padding=5, borderwidth=0, relief='flat')
        style.map('TButton', background=[('active', COLOR_ACCENT_ACTIVE)], foreground=[('active', COLOR_ACCENT_TEXT)])
        style.configure('Success.TButton', background=COLOR_SUCCESS, foreground=COLOR_SUCCESS_TEXT)
        style.map('Success.TButton', background=[('active', COLOR_ACCENT_ACTIVE)])
        style.configure('Error.TButton', background=COLOR_ERROR, foreground=COLOR_ACCENT_TEXT)
        style.map('Error.TButton', background=[('active', '#D35400')])
        style.configure('TEntry', insertcolor=COLOR_TEXT, fieldbackground=COLOR_WIDGET_BG)
        style.configure('Modern.Vertical.TScrollbar', troughcolor=COLOR_BACKGROUND, background=COLOR_ACCENT, borderwidth=0, arrowcolor=COLOR_ACCENT_TEXT)
        style.map('Modern.Vertical.TScrollbar', background=[('active', COLOR_ACCENT_ACTIVE)])
        style.configure('Accent.Horizontal.TProgressbar', troughcolor=COLOR_FRAME_BORDER, background=COLOR_ACCENT)

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.BOTH, expand=True)
        conn_frame = ttk.Frame(top_frame, padding=(10, 10, 10, 5))
        conn_frame.pack(fill=tk.X)

        ttk.Label(conn_frame, text="Server IP:").pack(side=tk.LEFT, padx=(0,5))
        self.ip_input = ttk.Entry(conn_frame, width=15, font=FONT_MONO, textvariable=self.ip_var)
        self.ip_var.trace_add("write", self.format_ip_as_typed)
        self.ip_input.insert(0, "127.0.0.1")
        self.ip_input.pack(side=tk.LEFT, padx=5)

        ttk.Label(conn_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_input = ttk.Entry(conn_frame, width=8)
        self.port_input.insert(0, "5000")
        self.port_input.pack(side=tk.LEFT, padx=5)

        self.password_label = ttk.Label(conn_frame, text="Password:")
        self.password_label.pack(side=tk.LEFT, padx=5)
        self.password_input = ttk.Entry(conn_frame, width=15, show="*", state="disabled")
        self.password_input.pack(side=tk.LEFT, padx=5)

        self.connect_btn = ttk.Button(conn_frame, text="🔗 Connect", command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=10)
        
        self.chat_btn = ttk.Button(conn_frame, text="💬 Chat with Server", command=self.open_chat_window, state="disabled")
        self.chat_btn.pack(side=tk.LEFT, padx=5)

        main_content_frame = ttk.Frame(top_frame, padding=(10, 5, 10, 10))
        main_content_frame.pack(fill=tk.BOTH, expand=True)
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(0, weight=1)
        files_frame = ttk.LabelFrame(main_content_frame, text="Available Files")
        files_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        files_frame.grid_rowconfigure(1, weight=1)
        files_frame.grid_columnconfigure(0, weight=1)

        filter_subframe = ttk.Frame(files_frame)
        filter_subframe.grid(row=0, column=0, sticky="ew", pady=(0,5))
        self.filter_entry = ttk.Entry(filter_subframe)
        self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,5))
        ttk.Button(filter_subframe, text="🔍 Filter", command=self.apply_filter).pack(side=tk.LEFT)
        
        ttk.Checkbutton(filter_subframe, text="Select All", variable=self.select_all_var, command=self.toggle_select_all).pack(side=tk.RIGHT, padx=5)

        list_subframe = ttk.Frame(files_frame)
        list_subframe.grid(row=1, column=0, sticky="nsew")
        canvas = tk.Canvas(list_subframe, bg=COLOR_WIDGET_BG, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_subframe, orient="vertical", command=canvas.yview, style='Modern.Vertical.TScrollbar')
        self.scrollable_frame = ttk.Frame(canvas, style="TFrame")
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side=tk.LEFT, fill="both", expand=True)

        action_frame = ttk.LabelFrame(main_content_frame, text="Download Options")
        action_frame.grid(row=0, column=1, sticky="nsew", ipadx=10)
        action_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(action_frame, text="Base Save Destination", font=FONT_BOLD).grid(row=0, column=0, sticky="w", pady=(0,5))
        path_display_frame = ttk.Frame(action_frame)
        path_display_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        path_display_frame.grid_columnconfigure(0, weight=1)
        ttk.Entry(path_display_frame, textvariable=self.save_directory_var, state='readonly').grid(row=0, column=0, sticky="ew")
        ttk.Button(path_display_frame, text="📁", command=self.browse_default_directory, width=3).grid(row=0, column=1, padx=(5,0))

        cb_new_folder = ttk.Checkbutton(action_frame, text="Download into a new sub-folder", variable=self.use_new_folder_var, command=self.toggle_new_folder_mode)
        cb_new_folder.grid(row=2, column=0, sticky="w", pady=(10, 5))
        new_folder_frame = ttk.Frame(action_frame)
        new_folder_frame.grid(row=3, column=0, sticky="ew")
        self.new_folder_name_entry = ttk.Entry(new_folder_frame, state='disabled')
        self.new_folder_name_entry.insert(0, "My Downloads")
        self.new_folder_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.create_folder_btn = ttk.Button(new_folder_frame, text="➕ Create", command=self.create_new_folder, state='disabled')
        self.create_folder_btn.pack(side=tk.LEFT)

        self.download_btn = ttk.Button(action_frame, text="⬇️ Download Selected", command=self.start_download, state='disabled')
        self.download_btn.grid(row=4, column=0, sticky="ew", ipady=5, pady=(20,0), padx=20)

        status_subframe = ttk.Frame(action_frame)
        status_subframe.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        status_subframe.grid_columnconfigure(0, weight=1)

        self.progress_label = ttk.Label(status_subframe, text="", anchor="center")
        self.progress_label.grid(row=0, column=0, sticky="ew", padx=10)
        self.status_label = ttk.Label(status_subframe, text="Status: Disconnected", anchor="center", wraplength=250)
        self.status_label.grid(row=1, column=0, sticky="ew")
        self.progress_bar = ttk.Progressbar(status_subframe, orient="horizontal", mode="determinate", style='Accent.Horizontal.TProgressbar')
        self.progress_bar.grid(row=2, column=0, sticky="ew", pady=5)

        exit_frame = ttk.Frame(self, padding=10)
        exit_frame.pack(fill=tk.X)
        self.exit_btn = ttk.Button(exit_frame, text="EXIT", command=self.handle_exit_button)
        self.exit_btn.pack(side=tk.RIGHT)

        self.back_btn = ttk.Button(exit_frame, text="↩️ Back to Launcher", command=self.go_to_launcher)
        self.back_btn.pack(side=tk.LEFT, padx=5)

    def format_ip_as_typed(self, *args):
        current_text = self.ip_var.get()
        cursor_pos = self.ip_input.index(tk.INSERT)
        
        # Sanitize input: allow only digits and dots
        sanitized_text = "".join(filter(lambda char: char.isdigit() or char == '.', current_text))
        
        # Prevent multiple dots
        while ".." in sanitized_text:
            sanitized_text = sanitized_text.replace("..", ".")
        
        parts = sanitized_text.split('.')
        
        # Limit each part to 3 digits and value to 255
        formatted_parts = []
        for part in parts:
            if len(part) > 3:
                part = part[:3]
            if part and int(part) > 255:
                part = "255"
            formatted_parts.append(part)
        
        # Limit to 4 parts
        formatted_parts = formatted_parts[:4]
        
        # Auto-add dot if an octet is complete and it's not the last one
        final_text = ""
        for i, part in enumerate(formatted_parts):
            final_text += part
            if len(part) == 3 and i < 3:
                final_text += "."
            elif len(part) < 3 and i < len(formatted_parts) - 1:
                final_text += "."
        
        # Update the entry only if text has changed
        if final_text != current_text:
            self.ip_var.set(final_text)
            # Try to restore cursor position
            if cursor_pos < len(final_text):
                self.ip_input.icursor(cursor_pos)

    def set_download_button_to_retry(self):
        self.download_btn.config(text="🔄 Retry Download", command=self.retry_download, state='normal')
    
    def set_download_button_to_new(self):
        self.download_btn.config(text="⬇️ Download Selected", command=self.start_download)
        if self.is_connected: self.download_btn.config(state='normal')

    def toggle_select_all(self):
        is_checked = self.select_all_var.get()
        for var in self.checkbuttons.values(): var.set(is_checked)

    def _recv_until_newline(self):
        data = b""
        while not data.endswith(b'\n'):
            chunk = self.client_socket.recv(1)
            if not chunk: raise ConnectionAbortedError("Socket connection broken")
            data += chunk
        return data.decode('utf-8').strip()

    def go_to_launcher(self):
        if self.is_connected and messagebox.askyesno("Confirm Navigation", "You are currently connected. \nDisconnect and return to launcher?"):
            self.disconnect_from_server()
            self.destroy()
            subprocess.run([sys.executable, "launcher.py"])
        elif not self.is_connected:
            self.destroy()
            subprocess.run([sys.executable, "launcher.py"])

    def connect_to_server(self):
        ip, port_str = self.ip_input.get(), self.port_input.get()
        if not ip or not port_str:
            messagebox.showerror("Error", "IP and Port cannot be empty.")
            return
        self.update_status("Connecting...", COLOR_ACCENT_ACTIVE)
        self.connect_btn.config(state='disabled')
        threading.Thread(target=self.connection_worker, args=(ip, int(port_str)), daemon=True).start()

    def connection_worker(self, ip, port):
        try:
            context = ssl.create_default_context(); context.check_hostname = False; context.verify_mode = ssl.CERT_NONE
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket = context.wrap_socket(sock, server_hostname=ip)
            self.client_socket.connect((ip, port))
            auth_req = self.client_socket.recv(1024).decode()
            if auth_req == 'NEEDS_PASS': self.after(0, self.ask_for_password)
            elif auth_req == 'NO_PASS': self.after(0, self.finish_login)
            else: raise ConnectionError(f"Unexpected response from server: {auth_req}")
        except Exception as e:
            self.after(0, self.disconnect_from_server)
            self.update_status(f"Connection Failed: {e}", COLOR_ERROR)
            messagebox.showerror("Error", f"Could not connect: {e}")

    def ask_for_password(self):
        self.update_status("Server requires password.", COLOR_ACCENT)
        self.password_input.config(state='normal')
        self.connect_btn.config(text="🔑 Login", command=self.login, state='normal')

    def login(self):
        password = self.password_input.get()
        if not password:
            messagebox.showerror("Error", "Password cannot be empty.")
            return
        self.connect_btn.config(state='disabled')
        threading.Thread(target=self.login_worker, args=(password,), daemon=True).start()

    def login_worker(self, password):
        try:
            self.client_socket.sendall(password.encode())
            response = self.client_socket.recv(1024).decode()
            if response == 'AUTH_SUCCESS': self.after(0, self.finish_login)
            else:
                self.after(0, lambda: messagebox.showerror("Error", "Authentication failed. Incorrect password."))
                self.after(0, self.disconnect_from_server)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Login failed: {e}"))
            self.after(0, self.disconnect_from_server)

    def finish_login(self):
        try:
            self.client_socket.send(b'LIST_FILES')
            files_json = self.client_socket.recv(4096).decode('utf-8')
            self.full_file_list = json.loads(files_json)
            self.populate_file_list(self.full_file_list)
            self.update_status("Connected. Ready to download.", COLOR_ACCENT)
            self.is_connected = True
            self.set_download_button_to_new()
            self.connect_btn.config(text='❌ Disconnect', command=self.toggle_connection, state='normal')
            self.update_exit_button_style()
            self.ip_input.config(state='disabled')
            self.port_input.config(state='disabled')
            self.password_input.config(state='disabled')
            self.connect_chat()
        except Exception as e:
            self.update_status(f"Connection Failed: {e}", COLOR_ERROR)
            self.disconnect_from_server()

    def create_new_folder(self):
        base_directory = self.save_directory_var.get()
        if "Please select" in base_directory: messagebox.showerror("Error", "Please select a base save folder first."); return
        new_folder_name = self.new_folder_name_entry.get()
        if not new_folder_name: messagebox.showerror("Error", "Please enter a name for the new folder."); return
        full_path = os.path.join(base_directory, new_folder_name)
        try:
            os.makedirs(full_path, exist_ok=True)
            self.specific_download_path = full_path
            self.new_folder_name_entry.config(state='disabled'); self.create_folder_btn.config(state='disabled')
            messagebox.showinfo("Success", f"Folder created at:\n{full_path}\nYou can now download into this folder.")
        except Exception as e: messagebox.showerror("Folder Creation Error", f"Could not create the folder: {e}")

    def toggle_new_folder_mode(self):
        new_state = 'normal' if self.use_new_folder_var.get() else 'disabled'
        self.new_folder_name_entry.config(state=new_state)
        self.create_folder_btn.config(state=new_state)
        if not self.use_new_folder_var.get(): self.specific_download_path = None

    def get_save_path(self):
        if self.use_new_folder_var.get():
            if not self.specific_download_path or not os.path.isdir(self.specific_download_path):
                messagebox.showerror("Error", "Please create the sub-folder using the 'Create' button first.")
                return None
            return self.specific_download_path
        else:
            save_directory = self.save_directory_var.get()
            if "Please select" in save_directory or not os.path.isdir(save_directory):
                messagebox.showerror("Error", "Please select a valid base save folder.")
                return None
            return save_directory

    def start_download(self):
        selected_files = [f for f, v in self.checkbuttons.items() if v.get()]
        if not selected_files: messagebox.showwarning("Warning", "Please select at least one file."); return
        save_path = self.get_save_path()
        if not save_path: return
        self.last_download_info = {"files": selected_files, "path": save_path}
        self.download_btn.config(state='disabled')
        threading.Thread(target=self.download_worker, args=(selected_files, save_path), daemon=True).start()

    def retry_download(self):
        if self.last_download_info:
            self.download_btn.config(state='disabled')
            threading.Thread(target=self.download_worker, args=(self.last_download_info["files"], self.last_download_info["path"]), daemon=True).start()

    def download_worker(self, files_to_download, save_path):
        try:
            self.client_socket.send(b'DOWNLOAD_FILES')
            self.client_socket.send(json.dumps(files_to_download).encode('utf-8'))
            for filename in files_to_download:
                file_buffer = self.download_single_file(filename)
                if file_buffer:
                    with open(os.path.join(save_path, filename), 'wb') as f: f.write(file_buffer.getvalue())
                else: raise ConnectionAbortedError(f"Download failed for {filename}.")
            final_msg = self._recv_until_newline()
            if 'END_OF_TRANSMISSION' in final_msg: self.update_status("All downloads completed! ✅", COLOR_ACCENT)
            else: self.update_status("Error: Unexpected final message from server.", COLOR_ERROR)
            self.after(0, self.set_download_button_to_new)
        except Exception as e:
            self.update_status(f"Download Error: {e}", COLOR_ERROR)
            self.after(0, self.set_download_button_to_retry)

    def download_single_file(self, filename):
        header = self._recv_until_newline()
        try: filename_from_server, filesize_str = header.strip().split(':', 1); filesize = int(filesize_str)
        except ValueError: raise ValueError(f"Invalid header from server: {header}")
        self.update_status(f"Downloading: {filename_from_server}", COLOR_ACCENT_ACTIVE)
        buffer = io.BytesIO()
        received_bytes = 0
        while received_bytes < filesize:
            chunk = self.client_socket.recv(min(4096, filesize - received_bytes))
            if not chunk: raise ConnectionAbortedError("Connection lost during download.")
            buffer.write(chunk)
            received_bytes += len(chunk)
            progress = int((received_bytes / filesize) * 100)
            self.update_progress(progress, f"{filename_from_server} ({progress}%)")
        self.client_socket.send(b'ACK')
        return buffer

    def handle_exit_button(self):
        if self.is_connected and not messagebox.askyesno("Exit Confirmation", "You are connected.\nAre you sure you want to disconnect and exit?"): return
        if self.is_connected: self.disconnect_from_server()
        self.destroy()

    def update_exit_button_style(self):
        self.exit_btn.config(style='Error.TButton' if self.is_connected else 'Success.TButton')

    def toggle_connection(self):
        if self.is_connected: self.disconnect_from_server()
        else: self.connect_to_server()

    def disconnect_from_server(self):
        self.is_connected = False
        for sock in [self.client_socket, self.chat_socket]:
            if sock:
                try: sock.close()
                except: pass
        self.client_socket, self.chat_socket = None, None
        self.full_file_list.clear()
        self.populate_file_list([])
        self.update_status("Disconnected", COLOR_TEXT)
        self.connect_btn.config(text='🔗 Connect', command=self.toggle_connection, state='normal')
        self.set_download_button_to_new()
        self.download_btn.config(state='disabled')
        if self.chat_window: self.chat_window.destroy(); self.chat_window = None
        self.chat_btn.config(state='disabled')
        self.progress_bar['value'] = 0; self.progress_label.config(text="")
        self.update_exit_button_style()
        self.ip_input.config(state='normal'); self.port_input.config(state='normal'); self.password_input.config(state='disabled')

    def browse_default_directory(self):
        directory = filedialog.askdirectory(title="Select Default Download Folder")
        if directory: self.save_directory_var.set(directory)

    def apply_filter(self):
        self.select_all_var.set(False)
        filter_text = self.filter_entry.get().lower().replace('.', '').strip()
        allowed = [ext.strip() for ext in filter_text.split(',')]
        filtered = self.full_file_list if not filter_text else [f for f in self.full_file_list if os.path.splitext(f)[1].lower().replace('.', '') in allowed]
        self.populate_file_list(filtered)

    def populate_file_list(self, file_list):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.checkbuttons.clear(); self.select_all_var.set(False)
        for filename in file_list:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.scrollable_frame, text=filename, variable=var)
            cb.pack(anchor='w', padx=10, pady=2, fill='x')
            self.checkbuttons[filename] = var

    def update_status(self, message, color): self.after(0, lambda: self.status_label.config(text=message, foreground=color))
    def update_progress(self, value, text): self.after(0, lambda: self._update_progress_gui(value, text))
    def _update_progress_gui(self, value, text): self.progress_bar['value'] = value; self.progress_label.config(text=text)

    def connect_chat(self):
        try:
            ip, chat_port = self.ip_input.get(), int(self.port_input.get()) + 1
            context = ssl.create_default_context(); context.check_hostname = False; context.verify_mode = ssl.CERT_NONE
            chat_sock_unwrapped = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.chat_socket = context.wrap_socket(chat_sock_unwrapped, server_hostname=ip)
            self.chat_socket.connect((ip, chat_port))
            self.chat_btn.config(state='normal')
            threading.Thread(target=self.listen_for_chat, daemon=True).start()
        except Exception as e: self.update_status(f"Chat connection failed: {e}", COLOR_ERROR)

    def listen_for_chat(self):
        while self.is_connected:
            try:
                data = self.chat_socket.recv(1024)
                if not data: break
                message = data.decode('utf-8')
                if message.startswith("MSG_S2C:"):
                    payload = message.split(":", 1)[1]
                    self.after(0, self.display_chat_message, "Server", payload)
                    self.after(0, self.show_chat_notification)
                elif message.startswith("WARN_S2C:"):
                    payload = message.split(":", 1)[1]
                    self.after(0, messagebox.showwarning, "Warning from Server", payload)
            except (ConnectionResetError, ssl.SSLError, socket.error): break
        self.after(0, self.chat_btn.config, {'state':'disabled'})
    
    def show_chat_notification(self):
        if not (self.chat_window and self.chat_window.winfo_exists()):
            current_text = self.chat_btn.cget("text")
            if "🔴" not in current_text: self.chat_btn.config(text="🔴 " + current_text)

    def clear_chat_notification(self):
        current_text = self.chat_btn.cget("text")
        if "🔴" in current_text: self.chat_btn.config(text=current_text.replace("🔴 ", ""))

    def open_chat_window(self):
        self.clear_chat_notification()
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.lift()
            return
        self.chat_window = tk.Toplevel(self)
        self.chat_window.title("Chat with Server"); self.chat_window.geometry("400x500"); self.chat_window.configure(bg=COLOR_BACKGROUND)
        chat_display = scrolledtext.ScrolledText(self.chat_window, state='disabled', wrap=tk.WORD, bg=COLOR_WIDGET_BG, fg=COLOR_TEXT)
        chat_display.pack(padx=10, pady=10, expand=True, fill='both')
        self.chat_window.chat_display = chat_display
        input_frame = ttk.Frame(self.chat_window)
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        msg_entry = ttk.Entry(input_frame)
        msg_entry.pack(side='left', fill='x', expand=True); msg_entry.focus()
        def send_chat_message_from_window():
            msg = msg_entry.get()
            if msg: self.send_chat_message(msg); msg_entry.delete(0, tk.END)
        send_btn = ttk.Button(input_frame, text="Send", command=send_chat_message_from_window)
        send_btn.pack(side='right', padx=(5,0))
        msg_entry.bind("<Return>", lambda event: send_chat_message_from_window())

    def display_chat_message(self, sender, message):
        if self.chat_window and self.chat_window.winfo_exists():
            display = self.chat_window.chat_display
            display.config(state='normal')
            display.insert(tk.END, f"[{sender}]: {message}\n")
            display.config(state='disabled'); display.see(tk.END)
    
    def send_chat_message(self, message):
        if self.chat_socket:
            try:
                self.chat_socket.sendall(f"MSG_C2S:{message}".encode('utf-8'))
                self.display_chat_message("You", message)
            except Exception as e: self.display_chat_message("System", f"Error sending message: {e}")

if __name__ == "__main__":
    app = ClientGUI()
    app.mainloop()