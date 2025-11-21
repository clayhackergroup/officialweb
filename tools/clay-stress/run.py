import asyncio
import aiohttp
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import json
from datetime import datetime
from collections import defaultdict
import statistics
import csv
import base64
from urllib.parse import urlparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class AdvancedStressTester:
    def __init__(self):
        self.running = False
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0,
            'response_times': [],
            'status_codes': defaultdict(int),
            'errors': defaultdict(int),
            'bytes_sent': 0,
            'bytes_received': 0,
            'start_time': None,
            'end_time': None
        }
        self.request_log = []
        
    async def make_request(self, session, method, url, headers, data, timeout, index):
        try:
            start = time.time()
            async with session.request(
                method, 
                url, 
                headers=headers, 
                data=data,
                timeout=aiohttp.ClientTimeout(total=timeout),
                ssl=False
            ) as resp:
                elapsed = time.time() - start
                content = await resp.read()
                
                self.stats['response_times'].append(elapsed)
                self.stats['status_codes'][resp.status] += 1
                self.stats['successful'] += 1
                self.stats['bytes_received'] += len(content)
                if data:
                    self.stats['bytes_sent'] += len(data) if isinstance(data, bytes) else len(str(data))
                
                self.request_log.append({
                    'index': index,
                    'status': resp.status,
                    'time': elapsed,
                    'timestamp': datetime.now(),
                    'size': len(content)
                })
                
                return resp.status, elapsed, len(content)
        except Exception as e:
            self.stats['failed'] += 1
            self.stats['errors'][type(e).__name__] += 1
            return None, str(e), 0
    
    async def run_test(self, url, method, headers, body, concurrent, duration, 
                      ramp_up=False, ramp_duration=10, proxy=None, rate_limit=None):
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0,
            'response_times': [],
            'status_codes': defaultdict(int),
            'errors': defaultdict(int),
            'bytes_sent': 0,
            'bytes_received': 0,
            'start_time': datetime.now(),
            'end_time': None
        }
        self.request_log = []
        
        connector = aiohttp.TCPConnector(limit=concurrent, limit_per_host=concurrent)
        timeout = aiohttp.ClientTimeout(total=30)
        
        kwargs = {'connector': connector, 'timeout': timeout}
        if proxy:
            kwargs['trust_env'] = False
            
        async with aiohttp.ClientSession(**kwargs) as session:
            start_time = time.time()
            tasks = []
            request_index = 0
            
            while time.time() - start_time < duration and self.running:
                # Ramp up logic
                current_concurrent = concurrent
                if ramp_up and time.time() - start_time < ramp_duration:
                    progress = (time.time() - start_time) / ramp_duration
                    current_concurrent = max(1, int(concurrent * progress))
                
                for _ in range(current_concurrent):
                    if time.time() - start_time >= duration:
                        break
                    
                    task = self.make_request(session, method, url, headers, body, 30, request_index)
                    tasks.append(task)
                    self.stats['total_requests'] += 1
                    request_index += 1
                    
                    # Rate limiting
                    if rate_limit:
                        await asyncio.sleep(1.0 / rate_limit)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks = []
                
                await asyncio.sleep(0.05)
            
            self.stats['total_time'] = time.time() - start_time
            self.stats['end_time'] = datetime.now()

class AdvancedStressTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 CLAY STRESS TEST - ADVANCED")
        self.root.geometry("1400x1000")
        self.tester = AdvancedStressTester()
        self.test_thread = None
        
        # Color scheme
        self.bg_dark = "#0f0f0f"
        self.bg_darker = "#050505"
        self.bg_card = "#1a1a1a"
        self.accent_blue = "#00d4ff"
        self.accent_green = "#00ff88"
        self.accent_red = "#ff0055"
        self.accent_orange = "#ffaa00"
        self.accent_purple = "#bb86fc"
        self.text_light = "#e8e8e8"
        self.text_muted = "#666666"
        
        self.root.configure(bg=self.bg_dark)
        
        self.setup_styles()
        self.create_notebook()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=self.bg_dark, foreground=self.text_light)
        style.configure('TLabel', background=self.bg_dark, foreground=self.text_light)
        style.configure('TLabelframe', background=self.bg_dark, foreground=self.text_light)
        style.configure('TLabelframe.Label', background=self.bg_dark, foreground=self.accent_blue)
        style.configure('TCheckbutton', background=self.bg_dark, foreground=self.text_light)
        style.configure('TRadiobutton', background=self.bg_dark, foreground=self.text_light)
        
        style.map('Start.TButton',
                  background=[('active', '#00ff99'), ('pressed', self.accent_green)])
        style.map('Stop.TButton',
                  background=[('active', '#ff4081'), ('pressed', self.accent_red)])
        style.map('Export.TButton',
                  background=[('active', '#ffbb33'), ('pressed', self.accent_orange)])
    
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Configuration
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ Configuration")
        self.setup_config_tab(config_frame)
        
        # Tab 2: Advanced Options
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="🔧 Advanced")
        self.setup_advanced_tab(advanced_frame)
        
        # Tab 3: Results
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📊 Results")
        self.setup_results_tab(results_frame)
        
        # Tab 4: Analytics
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📈 Analytics")
        self.setup_analytics_tab(analytics_frame)
    
    def setup_config_tab(self, parent):
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="⚡ CLAY ADVANCED STRESS TEST", 
                         font=("Courier New", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 20))
        
        # WARNING BOX
        warning_frame = ttk.LabelFrame(main_frame, text="⚠️ WARNING - READ BEFORE USE", padding="10")
        warning_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 15))
        warning_text = ttk.Label(warning_frame, text="This is a STRESS TEST tool. High loads can crash servers.\nStart with LOW values and increase gradually.\nOnly test on YOUR OWN infrastructure or with explicit permission.",
                                font=("Arial", 9), foreground=self.accent_red)
        warning_text.pack(anchor=tk.W)
        
        # URL
        ttk.Label(main_frame, text="🌐 Target URL:", font=("Arial", 11, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=8)
        self.url_var = tk.StringVar(value="https://example.com")
        ttk.Entry(main_frame, textvariable=self.url_var, width=80).grid(
            row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=8)
        
        # Method
        ttk.Label(main_frame, text="📋 Method:", font=("Arial", 11, "bold")).grid(
            row=2, column=0, sticky=tk.W)
        self.method_var = tk.StringVar(value="GET")
        method_frame = ttk.Frame(main_frame)
        method_frame.grid(row=2, column=1, columnspan=3, sticky=tk.W, pady=8)
        for method in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            ttk.Radiobutton(method_frame, text=method, variable=self.method_var, 
                           value=method).pack(side=tk.LEFT, padx=3)
        
        # Headers
        ttk.Label(main_frame, text="📝 Headers (JSON):", font=("Arial", 11, "bold")).grid(
            row=3, column=0, sticky=(tk.W, tk.N), pady=8)
        self.headers_text = scrolledtext.ScrolledText(main_frame, height=5, width=95,
                                                      bg=self.bg_card, fg=self.text_light,
                                                      insertbackground=self.accent_blue)
        self.headers_text.grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=8)
        self.headers_text.insert(tk.END, '{"User-Agent": "ClayAdvancedStressTester/2.0", "Accept": "*/*"}')
        
        # Body
        ttk.Label(main_frame, text="📦 Request Body:", font=("Arial", 11, "bold")).grid(
            row=4, column=0, sticky=(tk.W, tk.N), pady=8)
        self.body_text = scrolledtext.ScrolledText(main_frame, height=5, width=95,
                                                   bg=self.bg_card, fg=self.text_light,
                                                   insertbackground=self.accent_blue)
        self.body_text.grid(row=4, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=8)
        
        # Settings
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Load Test Settings (CONSERVATIVE DEFAULTS)", padding="15")
        settings_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=15)
        
        ttk.Label(settings_frame, text="Concurrent Connections (Max 1000):", 
                 font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.concurrent_var = tk.StringVar(value="10")
        ttk.Entry(settings_frame, textvariable=self.concurrent_var, width=15).grid(
            row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(settings_frame, text="Duration (seconds, Max 300):", 
                 font=("Arial", 10)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.duration_var = tk.StringVar(value="10")
        ttk.Entry(settings_frame, textvariable=self.duration_var, width=15).grid(
            row=0, column=3, sticky=tk.W, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=15)
        
        self.start_btn = ttk.Button(button_frame, text="▶ START TEST", 
                                   command=self.start_test, style='Start.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=8)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ STOP TEST", 
                                  command=self.stop_test, state=tk.DISABLED, 
                                  style='Stop.TButton')
        self.stop_btn.pack(side=tk.LEFT, padx=8)
        
        self.export_btn = ttk.Button(button_frame, text="💾 EXPORT RESULTS", 
                                    command=self.export_results, state=tk.NORMAL,
                                    style='Export.TButton')
        self.export_btn.pack(side=tk.LEFT, padx=8)
        
        main_frame.columnconfigure(1, weight=1)
    
    def setup_advanced_tab(self, parent):
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Authentication
        auth_frame = ttk.LabelFrame(main_frame, text="🔐 Authentication", padding="10")
        auth_frame.pack(fill=tk.X, pady=10)
        
        self.auth_type_var = tk.StringVar(value="none")
        ttk.Radiobutton(auth_frame, text="None", variable=self.auth_type_var, 
                       value="none").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(auth_frame, text="Basic Auth", variable=self.auth_type_var, 
                       value="basic").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(auth_frame, text="Bearer Token", variable=self.auth_type_var, 
                       value="bearer").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(auth_frame, text="Username:").pack(side=tk.LEFT, padx=5)
        self.auth_user = ttk.Entry(auth_frame, width=20)
        self.auth_user.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(auth_frame, text="Password/Token:").pack(side=tk.LEFT, padx=5)
        self.auth_pass = ttk.Entry(auth_frame, width=20, show="*")
        self.auth_pass.pack(side=tk.LEFT, padx=5)
        
        # Load Pattern
        pattern_frame = ttk.LabelFrame(main_frame, text="📊 Load Pattern", padding="10")
        pattern_frame.pack(fill=tk.X, pady=10)
        
        self.ramp_up_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(pattern_frame, text="Enable Ramp-Up", 
                       variable=self.ramp_up_var).pack(anchor=tk.W, padx=5)
        
        ttk.Label(pattern_frame, text="Ramp-Up Duration (seconds):").pack(side=tk.LEFT, padx=5)
        self.ramp_duration_var = tk.StringVar(value="10")
        ttk.Entry(pattern_frame, textvariable=self.ramp_duration_var, width=15).pack(
            side=tk.LEFT, padx=5)
        
        # Rate Limiting
        rate_frame = ttk.LabelFrame(main_frame, text="⏱️ Rate Limiting", padding="10")
        rate_frame.pack(fill=tk.X, pady=10)
        
        self.rate_limit_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(rate_frame, text="Enable Rate Limiting", 
                       variable=self.rate_limit_var).pack(anchor=tk.W, padx=5)
        
        ttk.Label(rate_frame, text="Requests Per Second:").pack(side=tk.LEFT, padx=5)
        self.rate_limit_rps = tk.StringVar(value="100")
        ttk.Entry(rate_frame, textvariable=self.rate_limit_rps, width=15).pack(
            side=tk.LEFT, padx=5)
        
        # SSL/TLS
        ssl_frame = ttk.LabelFrame(main_frame, text="🔒 SSL/TLS", padding="10")
        ssl_frame.pack(fill=tk.X, pady=10)
        
        self.verify_ssl_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(ssl_frame, text="Verify SSL Certificate", 
                       variable=self.verify_ssl_var).pack(anchor=tk.W, padx=5)
        
        # Proxy
        proxy_frame = ttk.LabelFrame(main_frame, text="🔗 Proxy", padding="10")
        proxy_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(proxy_frame, text="Proxy URL:").pack(side=tk.LEFT, padx=5)
        self.proxy_var = tk.StringVar(value="")
        ttk.Entry(proxy_frame, textvariable=self.proxy_var, width=50).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def setup_results_tab(self, parent):
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(main_frame, height=35, width=150,
                                                      bg=self.bg_card, fg=self.accent_green,
                                                      insertbackground=self.accent_blue,
                                                      font=("Courier New", 9))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.results_text.tag_config("success", foreground=self.accent_green, font=("Courier New", 9, "bold"))
        self.results_text.tag_config("error", foreground=self.accent_red, font=("Courier New", 9, "bold"))
        self.results_text.tag_config("warning", foreground=self.accent_orange, font=("Courier New", 9, "bold"))
        self.results_text.tag_config("info", foreground=self.accent_blue, font=("Courier New", 9, "bold"))
        self.results_text.tag_config("header", foreground=self.accent_purple, font=("Courier New", 10, "bold"))
        self.results_text.tag_config("stat", foreground=self.accent_blue, font=("Courier New", 9))
    
    def setup_analytics_tab(self, parent):
        main_frame = ttk.Frame(parent, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.analytics_frame = main_frame
        self.analytics_label = ttk.Label(main_frame, text="Run a test to see analytics...",
                                        font=("Arial", 12))
        self.analytics_label.pack(pady=20)
    
    def start_test(self):
        try:
            url = self.url_var.get()
            method = self.method_var.get()
            concurrent = int(self.concurrent_var.get())
            duration = int(self.duration_var.get())
            
            # Safety limits
            if concurrent > 1000:
                messagebox.showerror("Error", "Max concurrent connections is 1000")
                return
            
            if duration > 300:
                messagebox.showerror("Error", "Max duration is 300 seconds (5 minutes)")
                return
            
            if not url:
                messagebox.showerror("Error", "Please enter a target URL")
                return
            
            # Confirm before running high-load tests
            if concurrent > 100 or duration > 60:
                response = messagebox.askyesnocancel(
                    "⚠️ HIGH LOAD WARNING",
                    f"You are about to send:\n\n"
                    f"- {concurrent} concurrent connections\n"
                    f"- For {duration} seconds\n\n"
                    f"This could crash the server if it's not designed for this load.\n"
                    f"Make sure you have permission to test this server.\n\n"
                    f"Continue?"
                )
                if response is not True:
                    return
            
            try:
                headers = json.loads(self.headers_text.get("1.0", tk.END))
            except:
                headers = {}
            
            # Add authentication
            if self.auth_type_var.get() != "none":
                if self.auth_type_var.get() == "basic":
                    credentials = f"{self.auth_user.get()}:{self.auth_pass.get()}"
                    encoded = base64.b64encode(credentials.encode()).decode()
                    headers["Authorization"] = f"Basic {encoded}"
                elif self.auth_type_var.get() == "bearer":
                    headers["Authorization"] = f"Bearer {self.auth_pass.get()}"
            
            body = self.body_text.get("1.0", tk.END).strip() or None
            proxy = self.proxy_var.get() or None
            ramp_up = self.ramp_up_var.get()
            ramp_duration = int(self.ramp_duration_var.get()) if ramp_up else 0
            rate_limit = int(self.rate_limit_rps.get()) if self.rate_limit_var.get() else None
            
            self.results_text.delete("1.0", tk.END)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.results_text.insert(tk.END, f"[{timestamp}] ", "info")
            self.results_text.insert(tk.END, "Starting advanced stress test...\n\n", "success")
            self.results_text.insert(tk.END, f"URL: {url}\n", "info")
            self.results_text.insert(tk.END, f"Method: {method}\n", "info")
            self.results_text.insert(tk.END, f"Concurrent: {concurrent}\n", "info")
            self.results_text.insert(tk.END, f"Duration: {duration}s\n\n", "info")
            
            self.tester.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.test_thread = threading.Thread(
                target=self.run_test_thread,
                args=(url, method, headers, body, concurrent, duration, ramp_up, 
                      ramp_duration, proxy, rate_limit)
            )
            self.test_thread.start()
        
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def run_test_thread(self, url, method, headers, body, concurrent, duration, 
                       ramp_up, ramp_duration, proxy, rate_limit):
        try:
            asyncio.run(self.tester.run_test(url, method, headers, body, concurrent, 
                                            duration, ramp_up, ramp_duration, proxy, rate_limit))
            self.update_results()
            self.update_analytics()
        except Exception as e:
            self.results_text.insert(tk.END, f"\nError: {str(e)}\n", "error")
        finally:
            self.tester.running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def stop_test(self):
        self.tester.running = False
    
    def update_results(self):
        stats = self.tester.stats
        
        self.results_text.insert(tk.END, "=" * 80 + "\n", "header")
        self.results_text.insert(tk.END, "COMPREHENSIVE TEST RESULTS\n", "header")
        self.results_text.insert(tk.END, "=" * 80 + "\n\n", "header")
        
        # Performance Metrics
        self.results_text.insert(tk.END, "📊 PERFORMANCE METRICS\n", "header")
        self.results_text.insert(tk.END, "-" * 80 + "\n", "info")
        
        self.results_text.insert(tk.END, f"Total Requests:        ", "stat")
        self.results_text.insert(tk.END, f"{stats['total_requests']}\n", "success")
        
        self.results_text.insert(tk.END, f"Successful Requests:   ", "stat")
        self.results_text.insert(tk.END, f"{stats['successful']}\n", "success")
        
        self.results_text.insert(tk.END, f"Failed Requests:       ", "stat")
        color = "error" if stats['failed'] > 0 else "success"
        self.results_text.insert(tk.END, f"{stats['failed']}\n", color)
        
        success_rate = (stats['successful'] / max(stats['total_requests'], 1)) * 100
        self.results_text.insert(tk.END, f"Success Rate:          ", "stat")
        self.results_text.insert(tk.END, f"{success_rate:.2f}%\n\n", "success")
        
        # Timing Metrics
        self.results_text.insert(tk.END, "⏱️ TIMING METRICS\n", "header")
        self.results_text.insert(tk.END, "-" * 80 + "\n", "info")
        
        self.results_text.insert(tk.END, f"Total Test Duration:   ", "stat")
        self.results_text.insert(tk.END, f"{stats['total_time']:.2f}s\n", "success")
        
        rps = stats['total_requests'] / max(stats['total_time'], 0.1)
        self.results_text.insert(tk.END, f"Requests Per Second:   ", "stat")
        self.results_text.insert(tk.END, f"{rps:.2f} RPS\n\n", "success")
        
        # Response Time Statistics
        if stats['response_times']:
            self.results_text.insert(tk.END, "📈 RESPONSE TIME STATISTICS\n", "header")
            self.results_text.insert(tk.END, "-" * 80 + "\n", "info")
            
            response_times = stats['response_times']
            self.results_text.insert(tk.END, f"Min Response Time:     ", "stat")
            self.results_text.insert(tk.END, f"{min(response_times):.4f}s\n", "success")
            
            self.results_text.insert(tk.END, f"Max Response Time:     ", "stat")
            self.results_text.insert(tk.END, f"{max(response_times):.4f}s\n", "warning")
            
            avg_time = sum(response_times) / len(response_times)
            self.results_text.insert(tk.END, f"Average Response Time: ", "stat")
            self.results_text.insert(tk.END, f"{avg_time:.4f}s\n", "success")
            
            median_time = statistics.median(response_times)
            self.results_text.insert(tk.END, f"Median Response Time:  ", "stat")
            self.results_text.insert(tk.END, f"{median_time:.4f}s\n", "success")
            
            std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            self.results_text.insert(tk.END, f"Std Deviation:         ", "stat")
            self.results_text.insert(tk.END, f"{std_dev:.4f}s\n", "info")
            
            p95 = np.percentile(response_times, 95)
            p99 = np.percentile(response_times, 99)
            self.results_text.insert(tk.END, f"95th Percentile:       ", "stat")
            self.results_text.insert(tk.END, f"{p95:.4f}s\n", "warning")
            
            self.results_text.insert(tk.END, f"99th Percentile:       ", "stat")
            self.results_text.insert(tk.END, f"{p99:.4f}s\n\n", "warning")
        
        # Data Transfer
        self.results_text.insert(tk.END, "📡 DATA TRANSFER\n", "header")
        self.results_text.insert(tk.END, "-" * 80 + "\n", "info")
        
        self.results_text.insert(tk.END, f"Bytes Sent:            ", "stat")
        self.results_text.insert(tk.END, f"{stats['bytes_sent'] / 1024:.2f} KB\n", "success")
        
        self.results_text.insert(tk.END, f"Bytes Received:        ", "stat")
        self.results_text.insert(tk.END, f"{stats['bytes_received'] / 1024:.2f} KB\n", "success")
        
        total_bytes = (stats['bytes_sent'] + stats['bytes_received']) / (1024 * 1024)
        self.results_text.insert(tk.END, f"Total Data:            ", "stat")
        self.results_text.insert(tk.END, f"{total_bytes:.2f} MB\n\n", "success")
        
        # Status Codes
        self.results_text.insert(tk.END, "🔢 STATUS CODES\n", "header")
        self.results_text.insert(tk.END, "-" * 80 + "\n", "info")
        
        for code, count in sorted(stats['status_codes'].items()):
            color = "success" if 200 <= code < 300 else "warning" if 300 <= code < 400 else "error"
            percentage = (count / max(stats['total_requests'], 1)) * 100
            self.results_text.insert(tk.END, f"  {code}: {count:6d} ({percentage:5.2f}%)\n", color)
        
        # Errors
        if stats['errors']:
            self.results_text.insert(tk.END, "\n⚠️ ERROR BREAKDOWN\n", "header")
            self.results_text.insert(tk.END, "-" * 80 + "\n", "info")
            
            for error, count in sorted(stats['errors'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / max(stats['total_requests'], 1)) * 100
                self.results_text.insert(tk.END, f"  {error}: {count} ({percentage:.2f}%)\n", "warning")
        
        self.results_text.insert(tk.END, "\n" + "=" * 80 + "\n", "header")
    
    def update_analytics(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()
        
        stats = self.tester.stats
        
        if not stats['response_times']:
            ttk.Label(self.analytics_frame, text="No data to display").pack(pady=20)
            return
        
        fig = Figure(figsize=(14, 8), facecolor=self.bg_dark, edgecolor=self.accent_blue)
        
        # Response time distribution
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.hist(stats['response_times'], bins=50, color=self.accent_blue, edgecolor=self.accent_green)
        ax1.set_title("Response Time Distribution", color=self.text_light, fontsize=12, fontweight='bold')
        ax1.set_xlabel("Response Time (s)", color=self.text_light)
        ax1.set_ylabel("Frequency", color=self.text_light)
        ax1.tick_params(colors=self.text_light)
        ax1.grid(True, alpha=0.3)
        fig.patch.set_facecolor(self.bg_dark)
        ax1.set_facecolor(self.bg_card)
        
        # Status codes pie chart
        ax2 = fig.add_subplot(2, 2, 2)
        codes = list(stats['status_codes'].keys())
        counts = list(stats['status_codes'].values())
        colors = [self.accent_green if 200 <= c < 300 else self.accent_orange if 300 <= c < 400 else self.accent_red for c in codes]
        ax2.pie(counts, labels=codes, autopct='%1.1f%%', colors=colors)
        ax2.set_title("Status Code Distribution", color=self.text_light, fontsize=12, fontweight='bold')
        ax2.set_facecolor(self.bg_card)
        
        # Response times timeline
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.plot(stats['response_times'], color=self.accent_blue, linewidth=1.5, alpha=0.7)
        ax3.set_title("Response Time Over Time", color=self.text_light, fontsize=12, fontweight='bold')
        ax3.set_xlabel("Request #", color=self.text_light)
        ax3.set_ylabel("Response Time (s)", color=self.text_light)
        ax3.tick_params(colors=self.text_light)
        ax3.grid(True, alpha=0.3)
        ax3.set_facecolor(self.bg_card)
        
        # Percentile chart
        ax4 = fig.add_subplot(2, 2, 4)
        percentiles = [50, 75, 90, 95, 99]
        values = [np.percentile(stats['response_times'], p) for p in percentiles]
        bars = ax4.bar([str(p) for p in percentiles], values, color=self.accent_orange, edgecolor=self.accent_green)
        ax4.set_title("Response Time Percentiles", color=self.text_light, fontsize=12, fontweight='bold')
        ax4.set_xlabel("Percentile", color=self.text_light)
        ax4.set_ylabel("Response Time (s)", color=self.text_light)
        ax4.tick_params(colors=self.text_light)
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.set_facecolor(self.bg_card)
        
        canvas = FigureCanvasTkAgg(fig, master=self.analytics_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def export_results(self):
        if not self.tester.stats['response_times']:
            messagebox.showwarning("Warning", "No test results to export")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Request #', 'Status', 'Response Time (s)', 'Timestamp', 'Bytes'])
                
                for log in self.tester.request_log:
                    writer.writerow([log['index'], log['status'], f"{log['time']:.4f}", 
                                   log['timestamp'], log['size']])
            
            messagebox.showinfo("Success", f"Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    gui = AdvancedStressTestGUI(root)
    root.mainloop()
