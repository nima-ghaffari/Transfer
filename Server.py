import os
import socket
import threading
import json
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import ssl
import subprocess
import sys
import pandas as pd
import http.server
import socketserver

# --- Constants ---
FONT_FAMILY = "Segoe UI"
FONT_NORMAL = (FONT_FAMILY, 9)
FONT_BOLD = (FONT_FAMILY, 10, "bold")
FONT_IP = ("Consolas", 12, "bold")

COLOR_BACKGROUND = "#000F08"
COLOR_FRAME_BG = "#0E1F18"
COLOR_WIDGET_BG = "#03140D"
COLOR_TEXT = "#F0F0F0"
COLOR_ACCENT = "#136F63"
COLOR_ACCENT_ACTIVE = "#1AAE95"
COLOR_HOVER_BG = "#FFFFFF"
COLOR_HOVER_TEXT = "#000000"
COLOR_ACCENT_TEXT = "#FFFFFF"
COLOR_STATUS_RUNNING = "#1AAE95"
COLOR_STATUS_STOPPED = "#C74242"
COLOR_DANGER = "#D32F2F"

# --- Protocol Commands ---
CMD_LIST_FILES = "LIST_FILES"
CMD_DOWNLOAD_FILES = "DOWNLOAD_FILES"
PREFIX_MSG_C2S = "MSG_C2S:"
PREFIX_MSG_S2C = "MSG_S2C:"
PREFIX_WARN_S2C = "WARN_S2C:"

# --- Helper Classes ---
class SecureHTTPServer(http.server.HTTPServer):
    def __init__(self, server_address, HandlerClass, ssl_context):
        super().__init__(server_address, HandlerClass)
        self.ssl_context = ssl_context
        self.socket = self.ssl_context.wrap_socket(self.socket, server_side=True)

class ServerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Server")
        self.geometry("950x700")
        self.minsize(850, 650)
        self.configure(bg=COLOR_BACKGROUND)

        self.setup_styles()

        self.server = FileServer(self)
        self.log_data = []
        self.chat_histories = {}
        self.open_chat_windows = {}
        self.unread_messages = set()
        self.selected_path_var = tk.StringVar(value="No file or directory selected.")
        self.share_mode_var = tk.StringVar(value='directory')
        self.require_password_var = tk.BooleanVar(value=False)
        self.show_password_var = tk.BooleanVar(value=False)
        self.confirmed_password = None

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('.', background=COLOR_BACKGROUND, foreground=COLOR_TEXT, font=FONT_NORMAL)
        style.configure('TLabel', background=COLOR_BACKGROUND, foreground=COLOR_TEXT)
        style.configure('TFrame', background=COLOR_BACKGROUND)
        style.configure('TLabelFrame', background=COLOR_FRAME_BG, borderwidth=1, relief='solid')
        style.configure('TLabelFrame.Label', background=COLOR_FRAME_BG, foreground=COLOR_ACCENT_ACTIVE, font=FONT_BOLD, padding=(8, 4))
        style.configure('TNotebook', background=COLOR_BACKGROUND, borderwidth=0)
        style.configure('TNotebook.Tab', background=COLOR_ACCENT, foreground=COLOR_ACCENT_TEXT, font=FONT_BOLD, padding=[12, 6], borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', COLOR_ACCENT_ACTIVE), ('active', COLOR_ACCENT)])
        style.configure('TButton', background=COLOR_ACCENT, foreground=COLOR_ACCENT_TEXT, font=FONT_BOLD, padding=8, borderwidth=0, relief='flat')
        style.map('TButton', background=[('active', COLOR_HOVER_BG)], foreground=[('active', COLOR_HOVER_TEXT)])
        style.configure('Danger.TButton', background=COLOR_DANGER, foreground=COLOR_ACCENT_TEXT)
        style.map('Danger.TButton', background=[('active', COLOR_DANGER)])
        style.configure('TEntry', fieldbackground=COLOR_WIDGET_BG, foreground=COLOR_TEXT, insertcolor=COLOR_TEXT, borderwidth=2, relief='flat')
        style.map('TEntry', bordercolor=[('focus', COLOR_ACCENT_ACTIVE)], relief=[('focus', 'solid')])
        style.configure('Treeview', rowheight=25, fieldbackground=COLOR_WIDGET_BG, background=COLOR_WIDGET_BG, borderwidth=0, relief='flat')
        style.configure('Treeview.Heading', background=COLOR_ACCENT, foreground=COLOR_ACCENT_TEXT, font=FONT_BOLD, relief='flat', padding=6)
        style.map('Treeview.Heading', background=[('active', COLOR_ACCENT_ACTIVE)])
        style.map('Treeview', background=[('selected', COLOR_ACCENT_ACTIVE)], foreground=[('selected', COLOR_ACCENT_TEXT)])
        style.configure('TRadiobutton', background=COLOR_FRAME_BG, font=FONT_NORMAL)
        style.map('TRadiobutton', indicatorbackground=[('selected', COLOR_ACCENT_ACTIVE), ('!selected', '#555')])
        style.configure('TCheckbutton', background=COLOR_FRAME_BG, font=FONT_NORMAL)

    def create_widgets(self):
        exit_frame = ttk.Frame(self, padding=(10, 5, 10, 5))
        exit_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.exit_btn = ttk.Button(exit_frame, text="EXIT", command=self.on_closing, width=8)
        self.exit_btn.pack(side=tk.RIGHT)
        self.exit_btn.bind("<Enter>", self.on_exit_hover)
        self.exit_btn.bind("<Leave>", self.on_exit_leave)
        self.back_btn = ttk.Button(exit_frame, text="↩️ Back to Launcher", command=self.go_to_launcher)
        self.back_btn.pack(side=tk.LEFT, padx=5)
        self.back_btn.bind("<Enter>", self.on_back_hover)
        self.back_btn.bind("<Leave>", self.on_back_leave)

        main_frame = ttk.Frame(self)
        main_frame.pack(padx=10, pady=(10,0), fill=tk.BOTH, expand=True)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        control_tab = ttk.Frame(self.notebook, padding=10)
        management_tab = ttk.Frame(self.notebook, padding=10)
        chat_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(control_tab, text=' ⚙️  Control Panel  ')
        self.notebook.add(management_tab, text=' 👥  Client Management  ')
        self.notebook.add(chat_tab, text=' 💬  Chats  ')
        self.notebook.bind("<<TNotebookTabChanged>>", self.on_tab_changed)
        self.create_control_tab(control_tab)
        self.create_management_tab(management_tab)
        self.create_chat_tab(chat_tab)

    def on_exit_hover(self, event):
        if self.server.running: self.exit_btn.config(style='Danger.TButton')
    
    def on_exit_leave(self, event):
        self.exit_btn.config(style='TButton')

    def on_back_hover(self, event):
        if self.server.running: self.back_btn.config(style='Danger.TButton')
    
    def on_back_leave(self, event):
        self.back_btn.config(style='TButton')

    def on_tab_changed(self, event):
        if self.notebook.index(self.notebook.select()) == 2: self.clear_chat_notification()

    def show_chat_notification(self, client_ip):
        self.unread_messages.add(client_ip)
        current_text = self.notebook.tab(2, "text")
        if "🔴" not in current_text: self.notebook.tab(2, text=current_text.replace("💬", "🔴💬"))
    
    def clear_chat_notification(self, client_ip=None):
        if client_ip: self.unread_messages.discard(client_ip)
        if not self.unread_messages:
            current_text = self.notebook.tab(2, "text")
            if "🔴" in current_text: self.notebook.tab(2, text=current_text.replace("🔴", ""))

    def go_to_launcher(self):
        if self.server.running:
            messagebox.showwarning("Server is Running", "Please stop the server before going back to the launcher.")
            return
        self.destroy()
        subprocess.run([sys.executable, "launcher.py"])

    def create_control_tab(self, tab):
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(3, weight=1)
        share_frame = ttk.LabelFrame(tab, text="Share Configuration")
        share_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        share_frame.columnconfigure(1, weight=1)
        ttk.Radiobutton(share_frame, text="Share Directory", variable=self.share_mode_var, value='directory').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Radiobutton(share_frame, text="Share Single File", variable=self.share_mode_var, value='file').grid(row=0, column=1, padx=5, pady=5, sticky='w')
        ttk.Button(share_frame, text="Browse...", command=self.browse_path).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        path_label = ttk.Label(share_frame, textvariable=self.selected_path_var, font=FONT_NORMAL, wraplength=500, foreground=COLOR_ACCENT_ACTIVE, background=COLOR_FRAME_BG)
        path_label.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        settings_frame = ttk.LabelFrame(tab, text="Server Settings")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        ttk.Label(settings_frame, text="Port:", background=COLOR_FRAME_BG).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.port_input = ttk.Entry(settings_frame, width=8)
        self.port_input.insert(0, "5000")
        self.port_input.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        ttk.Label(settings_frame, text="Max Clients:", background=COLOR_FRAME_BG).grid(row=0, column=2, padx=(15, 5), pady=5, sticky='w')
        self.max_clients_input = ttk.Entry(settings_frame, width=8)
        self.max_clients_input.insert(0, "10")
        self.max_clients_input.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        password_checkbox = ttk.Checkbutton(settings_frame, text="Require Password", variable=self.require_password_var, command=self.toggle_password_fields)
        password_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.password_input = ttk.Entry(settings_frame, width=15, show="*", state='disabled')
        self.password_input.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        self.show_password_checkbox = ttk.Checkbutton(settings_frame, text="Show", variable=self.show_password_var, command=self.toggle_show_password, state='disabled')
        self.show_password_checkbox.grid(row=1, column=4, padx=5, pady=5, sticky='w')
        self.confirm_password_btn = ttk.Button(settings_frame, text="Confirm Password", command=self.confirm_password, state='disabled')
        self.confirm_password_btn.grid(row=2, column=0, columnspan=5, pady=5)
        control_status_frame = ttk.Frame(tab)
        control_status_frame.grid(row=2, column=0, sticky="ew", pady=(15, 10))
        control_status_frame.columnconfigure(2, weight=1)
        self.toggle_btn = ttk.Button(control_status_frame, text="▶️ Start", command=self.toggle_server, width=12)
        self.toggle_btn.grid(row=0, column=0, rowspan=3, sticky='ns')
        self.pause_btn = ttk.Button(control_status_frame, text="⏸️ Pause", command=self.pause_server_activity, state='disabled', width=12)
        self.pause_btn.grid(row=0, column=1, rowspan=3, padx=(8, 15), sticky='ns')
        self.status_label = ttk.Label(control_status_frame, text="Status: Stopped", font=FONT_BOLD, foreground=COLOR_STATUS_STOPPED)
        self.status_label.grid(row=0, column=2, sticky='w')
        self.ip_label = ttk.Label(control_status_frame, text="Server IP: -", font=FONT_IP, foreground=COLOR_ACCENT_ACTIVE)
        self.ip_label.grid(row=1, column=2, sticky='w', pady=(2,0))
        self.web_label = ttk.Label(control_status_frame, text="Web Access: -", font=FONT_NORMAL)
        self.web_label.grid(row=2, column=2, sticky='w')
        log_frame = ttk.LabelFrame(tab, text="Server Log")
        log_frame.grid(row=3, column=0, sticky="nsew")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_cols = ('Time', 'Category', 'Client IP', 'Details')
        self.log_tree = ttk.Treeview(log_frame, columns=log_cols, show='headings')
        for col in log_cols: self.log_tree.heading(col, text=col)
        self.log_tree.column('Time', width=80, anchor='center'); self.log_tree.column('Category', width=120, anchor='center'); self.log_tree.column('Client IP', width=120, anchor='center'); self.log_tree.column('Details', width=400)
        self.log_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        export_btn = ttk.Button(log_frame, text="Export Logs...", command=self.export_logs)
        export_btn.grid(row=1, column=0, pady=5)

    def create_management_tab(self, tab):
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        clients_frame = ttk.LabelFrame(tab, text="Connected Clients Monitor")
        clients_frame.grid(row=0, column=0, sticky="nsew")
        clients_frame.rowconfigure(0, weight=1)
        clients_frame.columnconfigure(0, weight=1)
        cols = ('Client IP', 'Status', 'Current File', 'Progress')
        self.clients_tree = ttk.Treeview(clients_frame, columns=cols, show='headings')
        for col in cols: self.clients_tree.heading(col, text=col)
        self.clients_tree.column('Client IP', width=120, anchor='center'); self.clients_tree.column('Status', width=120, anchor='center'); self.clients_tree.column('Current File', width=180, anchor='w'); self.clients_tree.column('Progress', width=80, anchor='center')
        self.clients_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        actions_frame = ttk.LabelFrame(tab, text="Client Actions")
        actions_frame.grid(row=1, column=0, sticky="ew", pady=(10,0))
        disconnect_btn = ttk.Button(actions_frame, text="❌ Disconnect Selected", command=self.disconnect_client)
        disconnect_btn.pack(side=tk.LEFT, padx=10, pady=5)
        send_warn_btn = ttk.Button(actions_frame, text="⚠️ Send Warning", command=self.send_warning_to_client)
        send_warn_btn.pack(side=tk.LEFT, padx=10, pady=5)

    def create_chat_tab(self, tab):
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        chat_list_frame = ttk.LabelFrame(tab, text="Online Clients for Chat")
        chat_list_frame.grid(row=0, column=0, sticky="nsew")
        chat_list_frame.rowconfigure(0, weight=1)
        chat_list_frame.columnconfigure(0, weight=1)
        self.chat_listbox = tk.Listbox(chat_list_frame, bg=COLOR_WIDGET_BG, fg=COLOR_TEXT, relief='flat', borderwidth=0, font=FONT_BOLD, selectbackground=COLOR_ACCENT_ACTIVE)
        self.chat_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        open_chat_btn = ttk.Button(chat_list_frame, text="Open Chat Window", command=self.open_chat_window_for_client)
        open_chat_btn.grid(row=1, column=0, pady=5)

    def open_chat_window_for_client(self):
        selected_indices = self.chat_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select a client from the list.")
            return
        
        client_ip = self.chat_listbox.get(selected_indices[0])
        self.clear_chat_notification(client_ip)

        if client_ip in self.open_chat_windows and self.open_chat_windows[client_ip]['window'].winfo_exists():
            self.open_chat_windows[client_ip]['window'].lift()
            return
        
        chat_window = tk.Toplevel(self)
        chat_window.title(f"Chat with {client_ip}")
        chat_window.geometry("400x500")
        chat_window.configure(bg=COLOR_BACKGROUND)
        chat_window.protocol("WM_DELETE_WINDOW", lambda ip=client_ip: self.on_chat_window_close(ip))
        chat_display = scrolledtext.ScrolledText(chat_window, state='disabled', wrap=tk.WORD, bg=COLOR_WIDGET_BG, fg=COLOR_TEXT)
        chat_display.pack(padx=10, pady=10, expand=True, fill='both')
        input_frame = ttk.Frame(chat_window)
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        msg_entry = ttk.Entry(input_frame)
        msg_entry.pack(side='left', fill='x', expand=True); msg_entry.focus()
        def send_message():
            payload = msg_entry.get()
            if payload and self.server.send_chat_message(client_ip, "MSG", payload):
                self.update_chat_display(client_ip, {'sender': 'Server', 'msg': payload})
                self.log_event("Chat", client_ip, f"Sent: '{payload}'")
                msg_entry.delete(0, tk.END)
        send_btn = ttk.Button(input_frame, text="Send", command=send_message)
        send_btn.pack(side='right', padx=(5,0))
        msg_entry.bind("<Return>", lambda event: send_message())
        self.open_chat_windows[client_ip] = {'window': chat_window, 'display': chat_display}
        self.update_chat_display(client_ip)

    def on_chat_window_close(self, client_ip):
        if client_ip in self.open_chat_windows:
            self.open_chat_windows[client_ip]['window'].destroy()
            del self.open_chat_windows[client_ip]

    def update_chat_display(self, ip, new_message=None):
        if ip not in self.chat_histories: self.chat_histories[ip] = []
        if new_message: self.chat_histories[ip].append(new_message)
        if ip in self.open_chat_windows and self.open_chat_windows[ip]['window'].winfo_exists():
            display_widget = self.open_chat_windows[ip]['display']
            display_widget.config(state='normal')
            display_widget.delete('1.0', tk.END)
            for entry in self.chat_histories.get(ip, []):
                display_widget.insert(tk.END, f"[{entry['sender']}]: {entry['msg']}\n")
            display_widget.see(tk.END)
            display_widget.config(state='disabled')

    def send_warning_to_client(self):
        if not self.clients_tree.selection():
            messagebox.showwarning("No Selection", "Please select a client from the Client Management list first.")
            return
        selected_item = self.clients_tree.selection()[0]
        client_ip = self.clients_tree.item(selected_item)['values'][0]
        payload = "You have received a warning from the administrator!"
        if self.server.send_chat_message(client_ip, "WARN", payload):
            self.log_event("Chat", client_ip, "Sent warning.")
            self.update_chat_display(client_ip, {'sender': 'Server (Warning)', 'msg': payload})
        else:
            messagebox.showerror("Error", f"Could not send warning. Client '{client_ip}' may not have a live chat connection.")
            self.log_event("Error", client_ip, "Failed to send warning.")
            
    def toggle_password_fields(self):
        state = 'normal' if self.require_password_var.get() else 'disabled'
        self.password_input.config(state=state)
        self.show_password_checkbox.config(state=state)
        self.confirm_password_btn.config(state=state)
        if state == 'disabled': self.confirmed_password = None; self.toggle_btn.config(state='normal')

    def toggle_show_password(self):
        self.password_input.config(show="" if self.show_password_var.get() else "*")

    def confirm_password(self):
        password = self.password_input.get()
        if not password:
            messagebox.showerror("Error", "Password cannot be empty.")
            return
        self.confirmed_password = password
        self.password_input.config(state='disabled'); self.confirm_password_btn.config(state='disabled')
        self.show_password_checkbox.config(state='disabled'); self.toggle_btn.config(state='normal')
        self.log_event(category="Security", details="Password has been set and confirmed.")

    def toggle_server(self):
        if not self.server.running:
            password_to_start = None
            if self.require_password_var.get():
                if not self.confirmed_password: messagebox.showerror("Error", "Please confirm the password before starting the server."); return
                password_to_start = self.confirmed_password
            try:
                port, max_clients = int(self.port_input.get()), int(self.max_clients_input.get())
            except ValueError:
                messagebox.showerror("Error", "Port and Max Clients must be valid numbers."); return
            success, msg = self.server.start(port, self.selected_path_var.get(), self.share_mode_var.get(), password_to_start, max_clients)
            if success:
                self.toggle_btn.config(text="⏹️ Stop"); self.pause_btn.config(state='normal')
                ip = self.server.get_local_ip()
                self.status_label.config(text="Status: Running", foreground=COLOR_STATUS_RUNNING)
                self.ip_label.config(text=f"Server IP: {ip}")
                self.web_label.config(text=f"Web Access: https://{ip}:{self.server.web_port}")
                self.log_event("Server Status", details=f"Server ({'Secure' if password_to_start else 'Open'} Mode) started on {ip}:{port}")
            else:
                self.log_event("Error", details=msg); messagebox.showerror("Error", msg)
        else:
            self.server.stop()
            self.toggle_btn.config(text="▶️ Start"); self.pause_btn.config(text='⏸️ Pause', state='disabled')
            self.status_label.config(text="Status: Stopped", foreground=COLOR_STATUS_STOPPED)
            self.ip_label.config(text="Server IP: -"); self.web_label.config(text="Web Access: -")
            self.log_event(category="Server Status", details="Server stopped")
            self.clients_tree.delete(*self.clients_tree.get_children())
            self.chat_listbox.delete(0, tk.END)
            self.toggle_password_fields()

    def pause_server_activity(self):
        if not self.server.running: return
        self.server.is_paused = not self.server.is_paused
        self.pause_btn.config(text=f"{'▶️ Resume' if self.server.is_paused else '⏸️ Pause'}")
        self.log_event("Server Status", details=f"Server activity {'Paused' if self.server.is_paused else 'Resumed'}.")

    def on_closing(self):
        if self.server.running: messagebox.showwarning("Server is Running", "Please stop the server before exiting."); return
        self.destroy()

    def browse_path(self):
        path = filedialog.askdirectory(title="Select Directory") if self.share_mode_var.get() == 'directory' else filedialog.askopenfilename(title="Select File")
        if path: self.selected_path_var.set(path)

    def disconnect_client(self):
        if not self.clients_tree.selection(): messagebox.showwarning("No Selection", "Please select a client to disconnect."); return
        client_ip = self.clients_tree.item(self.clients_tree.selection()[0])['values'][0]
        if client_ip in self.server.clients_info: self.server.clients_info[client_ip]['socket'].close()

    def log_event(self, category, ip="-", details=""):
        self.after(0, self._log_event_gui, category, ip, details)

    def _log_event_gui(self, category, ip, details):
        log_time = time.strftime('%H:%M:%S')
        log_entry = {'Time': log_time, 'Category': category, 'Client IP': ip, 'Details': details}
        self.log_data.append(log_entry)
        self.log_tree.insert("", tk.END, values=tuple(log_entry.values())); self.log_tree.yview_moveto(1)
        
    def export_logs(self):
        if not self.log_data: messagebox.showinfo("No Logs", "There is no log data to export."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx"), ("Text Files", "*.txt"), ("All Files", "*.*")], title="Save Logs As")
        if not filepath: return
        try:
            if filepath.endswith('.xlsx'): pd.DataFrame(self.log_data).to_excel(filepath, index=False, engine='openpyxl')
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('\t'.join(self.log_data[0].keys()) + '\n')
                    for entry in self.log_data: f.write('\t'.join(str(v) for v in entry.values()) + '\n')
            messagebox.showinfo("Success", f"Logs successfully exported to\n{filepath}")
        except Exception as e: messagebox.showerror("Export Error", f"Failed to export logs: {e}")

    def add_client_to_tree(self, ip):
        if ip not in self.chat_histories: self.chat_histories[ip] = []
        return self.clients_tree.insert("", tk.END, values=(ip, "Authenticating", "-", "0%"))

    def remove_client_from_tree(self, ip):
        if ip in self.server.clients_info and (tree_id := self.server.clients_info[ip].get('tree_id')):
            try: self.clients_tree.delete(tree_id)
            except tk.TclError: pass
    
    def add_client_to_chat_list(self, ip): self.chat_listbox.insert(tk.END, ip)

    def remove_client_from_chat_list(self, ip):
        try:
            items = self.chat_listbox.get(0, tk.END)
            if ip in items: self.chat_listbox.delete(items.index(ip))
        except tk.TclError: pass

    def _update_client_tree(self, ip, column_name, value):
        if ip in self.server.clients_info and (tree_id := self.server.clients_info[ip].get('tree_id')):
            try: self.clients_tree.set(tree_id, column_name, value)
            except tk.TclError: pass

    def update_client_status(self, ip, status): self.after(0, self._update_client_tree, ip, 'Status', status)
    def update_client_file(self, ip, filename): self.after(0, self._update_client_tree, ip, 'Current File', filename)
    def update_client_progress(self, ip, progress): self.after(0, self._update_client_tree, ip, 'Progress', progress)

class FileServer:
    def __init__(self, gui):
        self.gui = gui
        self.host = '0.0.0.0'
        self.port, self.chat_port, self.web_port = 0, 0, 0
        self.server_socket, self.chat_socket, self.web_server = None, None, None
        self.running, self.is_paused = False, False
        self.share_mode, self.shared_path = 'directory', ""
        self.clients_info, self.chat_clients, self.password, self.max_clients = {}, {}, None, 10
        self.ssl_context = None

    def _generate_certs(self):
        key_file, cert_file = "server.key", "server.crt"
        if os.path.exists(key_file) and os.path.exists(cert_file): return True, ""
        try:
            from OpenSSL import crypto
            pkey = crypto.PKey(); pkey.generate_key(crypto.TYPE_RSA, 2048)
            cert = crypto.X509(); cert.get_subject().CN = self.get_local_ip()
            cert.set_serial_number(1000); cert.gmtime_adj_notBefore(0); cert.gmtime_adj_notAfter(10*365*24*60*60)
            cert.set_issuer(cert.get_subject()); cert.set_pubkey(pkey); cert.sign(pkey, 'sha256')
            with open(cert_file, "wt") as f: f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf-8'))
            with open(key_file, "wt") as f: f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey).decode('utf-8'))
            return True, ""
        except ImportError: return False, "PyOpenSSL is required. Run: pip install pyopenssl"
        except Exception as e: return False, f"Could not generate SSL certs: {e}"

    def start(self, port, path, mode, password, max_clients):
        if not path or not os.path.exists(path): return False, "Selected path does not exist."
        certs_ok, msg = self._generate_certs();
        if not certs_ok: return False, msg
        
        self.port, self.chat_port, self.web_port = int(port), int(port) + 1, int(port) + 2
        self.shared_path, self.share_mode, self.password, self.max_clients = os.path.abspath(path), mode, password, int(max_clients)
        
        try:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")
            self.server_socket = self._create_listening_socket(self.port)
            self.chat_socket = self._create_listening_socket(self.chat_port)
            def handler_factory(directory, server_instance):
                class CustomHandler(http.server.SimpleHTTPRequestHandler):
                    def __init__(self, *args, **kwargs): super().__init__(*args, directory=directory, **kwargs)
                    def do_GET(self):
                        if server_instance.password:
                            self.send_response(403); self.send_header("Content-type", "text/html; charset=utf-8"); self.end_headers()
                            self.wfile.write(b"<h1>403 Forbidden</h1><p>Web access is disabled when server is password-protected.</p>")
                            return
                        super().do_GET()
                return CustomHandler
            handler = handler_factory(self.shared_path, self)
            self.web_server = SecureHTTPServer((self.host, self.web_port), handler, self.ssl_context)
            self.running = True
            threading.Thread(target=self.accept_connections, args=(self.server_socket, self.handle_file_client), daemon=True).start()
            threading.Thread(target=self.accept_connections, args=(self.chat_socket, self.handle_chat_client), daemon=True).start()
            threading.Thread(target=self.web_server.serve_forever, daemon=True).start()
            time.sleep(0.2)
            return True, ""
        except Exception as e: return False, str(e)

    def _create_listening_socket(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, port)); sock.listen(5)
        return self.ssl_context.wrap_socket(sock, server_side=True)

    def stop(self):
        self.running = False
        if self.web_server: self.web_server.shutdown(); self.web_server.server_close()
        for sock in [self.server_socket, self.chat_socket]:
            if sock: sock.close()
        for ip in list(self.clients_info.keys()):
            if self.clients_info[ip].get('socket'): self.clients_info[ip]['socket'].close()
        for ip in list(self.chat_clients.keys()):
            if self.chat_clients[ip]: self.chat_clients[ip].close()
        self.clients_info.clear(); self.chat_clients.clear()

    def accept_connections(self, listening_socket, handler_func):
        while self.running:
            try:
                client_socket, addr = listening_socket.accept()
                if self.is_paused or len(self.clients_info) >= self.max_clients and handler_func == self.handle_file_client:
                    client_socket.close()
                    continue
                threading.Thread(target=handler_func, args=(client_socket, addr[0]), daemon=True).start()
            except (socket.error, ssl.SSLError): break

    def handle_chat_client(self, chat_socket, ip):
        self.chat_clients[ip] = chat_socket
        self.gui.log_event("Chat", ip, "Chat connection established.")
        self.gui.after(0, self.gui.add_client_to_chat_list, ip)
        while self.running:
            try:
                data = chat_socket.recv(1024)
                if not data: break
                message = data.decode('utf-8')
                if message.startswith(PREFIX_MSG_C2S):
                    payload = message.split(":", 1)[1]
                    self.gui.log_event("Chat", ip, f"Received: '{payload}'")
                    self.gui.update_chat_display(ip, new_message={'sender':'Client', 'msg':payload})
                    if not (ip in self.gui.open_chat_windows and self.gui.open_chat_windows[ip]['window'].winfo_exists()):
                        self.gui.show_chat_notification(ip)
            except (ConnectionResetError, ssl.SSLError): break
        self.gui.log_event("Chat", ip, "Chat connection lost.")
        if ip in self.chat_clients: self.chat_clients[ip].close(); del self.chat_clients[ip]
        self.gui.after(0, self.gui.remove_client_from_chat_list, ip)

    def send_chat_message(self, ip, comm_type, payload):
        if ip in self.chat_clients:
            try:
                prefix = PREFIX_MSG_S2C if comm_type == "MSG" else PREFIX_WARN_S2C
                self.chat_clients[ip].sendall(f"{prefix}{payload}".encode('utf-8'))
                return True
            except (ConnectionResetError, BrokenPipeError): return False
        return False
        
    def handle_file_client(self, client_socket, client_ip):
        tree_id = self.gui.add_client_to_tree(client_ip)
        self.clients_info[client_ip] = {'socket': client_socket, 'tree_id': tree_id}
        try:
            self.gui.log_event("Connection", client_ip, "Authenticating...")
            if self.password:
                client_socket.sendall(b'NEEDS_PASS')
                client_socket.settimeout(10.0)
                password = client_socket.recv(1024).decode()
                if password != self.password:
                    client_socket.sendall(b"AUTH_FAILED"); self.gui.log_event("Authentication", client_ip, "Failed (Incorrect password)."); return
                client_socket.sendall(b"AUTH_SUCCESS"); self.gui.log_event("Authentication", client_ip, "Successful.")
            else:
                client_socket.sendall(b'NO_PASS'); self.gui.log_event("Authentication", client_ip, "Successful (No password).")
            self.gui.update_client_status(client_ip, "Connected")
            client_socket.settimeout(None)
            while self.running:
                command_bytes = client_socket.recv(1024)
                if not command_bytes: break
                command = command_bytes.decode()
                if command == CMD_LIST_FILES:
                    self.gui.update_client_status(client_ip, "Listing files")
                    files = [f for f in os.listdir(self.shared_path) if os.path.isfile(os.path.join(self.shared_path, f))] if self.share_mode == 'directory' else [os.path.basename(self.shared_path)]
                    client_socket.sendall(json.dumps(files).encode('utf-8'))
                    self.gui.update_client_status(client_ip, "Idle")
                elif command == CMD_DOWNLOAD_FILES:
                    requested_files = json.loads(client_socket.recv(4096).decode('utf-8'))
                    self.gui.log_event("File Transfer", client_ip, f"Requested {len(requested_files)} file(s).")
                    for filename in requested_files:
                        if os.path.basename(filename) != filename: continue
                        abs_shared, req_path = os.path.abspath(self.shared_path), os.path.join(os.path.abspath(self.shared_path), filename)
                        if self.share_mode == 'file': req_path = abs_shared
                        if not os.path.abspath(req_path).startswith(abs_shared) or not os.path.isfile(req_path): continue
                        self.gui.update_client_status(client_ip, "Downloading"); self.gui.update_client_file(client_ip, filename)
                        filesize = os.path.getsize(req_path)
                        client_socket.sendall(f"{filename}:{filesize}\n".encode('utf-8'))
                        with open(req_path, 'rb') as f:
                            sent_bytes = 0
                            while (chunk := f.read(4096)):
                                if self.is_paused: time.sleep(1)
                                client_socket.sendall(chunk)
                                sent_bytes += len(chunk)
                                self.gui.update_client_progress(client_ip, f"{int((sent_bytes/filesize)*100)}%")
                        client_socket.recv(1024)
                        self.gui.log_event("File Transfer", client_ip, f"Successfully sent '{filename}'.")
                    client_socket.sendall(b'END_OF_TRANSMISSION\n')
                    self.gui.update_client_status(client_ip, "Completed"); self.gui.update_client_file(client_ip, "-")
        except (socket.timeout, ConnectionResetError, ssl.SSLEOFError): self.gui.log_event("Error", client_ip, "Connection lost.")
        except Exception as e: self.gui.log_event("Error", client_ip, f"An unexpected error occurred: {e}")
        finally:
            self.gui.log_event("Connection", client_ip, "Client disconnected.")
            self.gui.update_client_status(client_ip, "Disconnected")
            self.gui.remove_client_from_tree(client_ip)
            if client_ip in self.clients_info: del self.clients_info[client_ip]
            client_socket.close()

    @staticmethod
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(0.1); s.connect(('8.8.8.8', 1)); IP = s.getsockname()[0]
        except Exception: IP = '127.0.0.1'
        finally: s.close()
        return IP

if __name__ == "__main__":
    app = ServerGUI()
    app.mainloop()