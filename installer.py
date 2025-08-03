import os
import sys
import shutil
import webbrowser
import zipfile
import winreg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkbootstrap import Style
from threading import Thread

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("抖音视频下载器安装程序")
        self.root.geometry("600x650")
        
        self.style = Style(theme="minty")
        
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(self.main_frame, text="抖音视频下载器安装向导", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # 安装路径选择
        path_frame = ttk.Frame(self.main_frame)
        path_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(path_frame, text="安装路径:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.path_var = tk.StringVar(value="C:\\Program Files\\DouyinDownloader")
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=40)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(path_frame, text="浏览", command=self.browse_directory).pack(side=tk.LEFT)
        
        # Chromedriver 下载引导
        self.chrome_frame = ttk.LabelFrame(self.main_frame, text="Chromedriver 安装", padding=10)
        self.chrome_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(self.chrome_frame, text="请按以下步骤操作:").pack(anchor=tk.W)
        
        steps = [
            "1. 点击下方按钮在浏览器中下载 chromedriver",
            "2. 下载完成后点击'选择文件'按钮",
            "3. 选择下载的 chromedriver-win32.zip 文件"
        ]
        
        for step in steps:
            ttk.Label(self.chrome_frame, text=step).pack(anchor=tk.W, padx=5, pady=2)
        
        btn_frame = ttk.Frame(self.chrome_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="在浏览器中下载", command=self.open_download_page, style="info.TButton").pack(side=tk.LEFT, padx=5)
        self.select_btn = ttk.Button(btn_frame, text="选择文件", command=self.select_chromedriver, state=tk.DISABLED, style="primary.TButton")
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        # 选项
        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        self.create_shortcut_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="创建桌面快捷方式", variable=self.create_shortcut_var).pack(anchor=tk.W)
        
        # 进度显示
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = ttk.Label(self.progress_frame, text="准备安装...", anchor=tk.CENTER)
        self.progress_label.pack(fill=tk.X)
        
        self.progress = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X)
        
        # 日志输出
        self.log_text = tk.Text(self.main_frame, height=8, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 操作按钮
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.install_btn = ttk.Button(btn_frame, text="开始安装", command=self.start_installation, style="success.TButton", state=tk.DISABLED)
        self.install_btn.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(btn_frame, text="取消", command=self.root.quit, style="danger.TButton").pack(side=tk.RIGHT)
        
        self.install_thread = None
        self.cancel_flag = False
        self.chromedriver_zip_path = None
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def update_progress(self, value, message=None):
        self.progress['value'] = value
        if message:
            self.progress_label.config(text=message)
        self.root.update()
    
    def get_chrome_version(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            winreg.CloseKey(key)
            return version
        except Exception as e:
            self.log_message(f"获取Chrome版本失败: {str(e)}")
            return None
    
    def open_download_page(self):
        chrome_version = self.get_chrome_version()
        if not chrome_version:
            messagebox.showerror("错误", "无法获取Chrome版本，请确保Chrome已安装")
            return
        
        major_version = int(chrome_version.split('.')[0])
        
        if major_version < 115:
            download_url = f"https://chromedriver.storage.googleapis.com/{chrome_version}/chromedriver_win32.zip"
        else:
            download_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chrome_version}/win32/chromedriver-win32.zip"
        
        self.log_message(f"请在浏览器中下载: {download_url}")
        webbrowser.open(download_url)
        self.select_btn.config(state=tk.NORMAL)
    
    def select_chromedriver(self):
        file_path = filedialog.askopenfilename(
            title="选择 chromedriver-win32.zip 文件",
            filetypes=[("ZIP 文件", "*.zip"), ("所有文件", "*.*")]
        )
        
        if file_path and file_path.endswith('.zip') and 'chromedriver' in os.path.basename(file_path).lower():
            self.chromedriver_zip_path = file_path
            self.log_message(f"已选择文件: {file_path}")
            self.install_btn.config(state=tk.NORMAL)
        else:
            messagebox.showerror("错误", "请选择正确的 chromedriver-win32.zip 文件")
    
    def extract_zip(self, zip_path, extract_to):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return True
        except Exception as e:
            self.log_message(f"解压失败: {str(e)}")
            return False
    
    def create_shortcut(self, target, shortcut_name):
        try:
            from win32com.client import Dispatch
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.IconLocation = target
            shortcut.save()
            return True
        except Exception as e:
            self.log_message(f"创建快捷方式失败: {str(e)}")
            return False
    
    def install_chromedriver(self, install_dir):
        if not self.chromedriver_zip_path:
            return False
    
        self.log_message("正在解压 chromedriver...")
        self.update_progress(30, "正在解压 chromedriver...")
    
        temp_dir = os.path.join(install_dir, "temp_chromedriver")
        os.makedirs(temp_dir, exist_ok=True)
    
        if not self.extract_zip(self.chromedriver_zip_path, temp_dir):
            return False
    
        chromedriver_path = None
        for root, dirs, files in os.walk(temp_dir):
            if "chromedriver.exe" in files:
                chromedriver_path = os.path.join(root, "chromedriver.exe")
                break
    
        if not chromedriver_path:
            self.log_message("未找到 chromedriver.exe")
            shutil.rmtree(temp_dir, ignore_errors=True)  
            return False
    
        target_path = os.path.join(install_dir, "chromedriver.exe")
        shutil.move(chromedriver_path, target_path)
    
        shutil.rmtree(temp_dir, ignore_errors=True)
    
        self.log_message(f"chromedriver 安装完成: {target_path}")
        return True
    
    def install_main_program(self, install_dir):
        try:
            source_path = get_resource_path("DouyinDownloader.exe")
            if not os.path.exists(source_path):
                self.log_message("错误: 找不到嵌入的主程序")
                return False
            
            target_path = os.path.join(install_dir, "DouyinDownloader.exe")
            
            os.makedirs(install_dir, exist_ok=True)
            
            shutil.copy(source_path, target_path)
            self.log_message(f"主程序已安装到: {target_path}")
            return target_path
        except Exception as e:
            self.log_message(f"安装主程序失败: {str(e)}")
            return None
    
    def perform_installation(self):
        self.update_progress(0, "正在准备安装...")
        
        install_dir = self.path_var.get()
        if not install_dir:
            messagebox.showerror("错误", "请选择安装目录")
            return
        
        try:
            os.makedirs(install_dir, exist_ok=True)
            
            self.update_progress(10, "正在安装 chromedriver...")
            if not self.install_chromedriver(install_dir):
                messagebox.showerror("错误", "chromedriver 安装失败")
                return
            
            self.update_progress(60, "正在安装主程序...")
            main_exe_path = self.install_main_program(install_dir)
            if not main_exe_path:
                messagebox.showerror("错误", "主程序安装失败")
                return
            
            if self.create_shortcut_var.get():
                self.update_progress(90, "正在创建快捷方式...")
                if self.create_shortcut(main_exe_path, "抖音视频下载器"):
                    self.log_message("桌面快捷方式创建成功")
                else:
                    self.log_message("桌面快捷方式创建失败")
            
            self.update_progress(100, "安装完成!")
            messagebox.showinfo("成功", "抖音视频下载器安装完成!")
            
        except Exception as e:
            self.log_message(f"安装过程中出错: {str(e)}")
            messagebox.showerror("错误", f"安装失败: {str(e)}")
    
    def start_installation(self):
        if self.install_thread and self.install_thread.is_alive():
            return
        
        self.install_thread = Thread(target=self.perform_installation, daemon=True)
        self.install_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()