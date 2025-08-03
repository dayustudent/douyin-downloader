import os
import time
import logging
import requests
import threading
import tkinter as tk
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from selenium.webdriver.chrome.service import Service
from tkinter import filedialog, messagebox, scrolledtext
from ttkbootstrap import Style, Frame, Label, Entry, Button, Progressbar, Combobox

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("douyin_downloader.log", encoding='utf-8')
    ]
)
logger = logging.getLogger('DouyinDownloader')

class DouyinDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("抖音视频下载器")
        self.root.geometry("800x600")
        
        # 应用ttkbootstrap主题
        self.style = Style(theme="minty")
        
        # 创建主框架
        self.main_frame = Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # URL输入部分
        url_frame = Frame(self.main_frame)
        url_frame.pack(fill=tk.X, pady=10)
        
        Label(url_frame, text="抖音视频URL:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.url_entry = Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.add_url_btn = Button(
            url_frame, 
            text="添加URL", 
            command=self.add_url,
            bootstyle="primary-outline"
        )
        self.add_url_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_btn = Button(
            url_frame, 
            text="选择URL文件", 
            command=self.load_url_file,
            bootstyle="secondary-outline"
        )
        self.file_btn.pack(side=tk.LEFT)
        
        # URL列表显示
        list_frame = Frame(self.main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        Label(list_frame, text="待下载列表:").pack(anchor=tk.W)
        
        self.url_listbox = tk.Listbox(
            list_frame, 
            height=8,
            selectmode=tk.EXTENDED
        )
        self.url_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 操作按钮
        btn_frame = Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.clear_btn = Button(
            btn_frame, 
            text="清除所选", 
            command=self.clear_selected,
            bootstyle="danger-outline"
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_all_btn = Button(
            btn_frame, 
            text="清空列表", 
            command=self.clear_all,
            bootstyle="danger"
        )
        self.clear_all_btn.pack(side=tk.LEFT)
        
        # 保存路径设置
        path_frame = Frame(self.main_frame)
        path_frame.pack(fill=tk.X, pady=10)
        
        Label(path_frame, text="保存路径:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.path_var = tk.StringVar()
        self.path_entry = Entry(path_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.browse_btn = Button(
            path_frame, 
            text="浏览", 
            command=self.browse_directory,
            bootstyle="info-outline"
        )
        self.browse_btn.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_frame = Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = Label(
            self.progress_frame, 
            text="就绪",
            anchor=tk.CENTER
        )
        self.progress_label.pack(fill=tk.X)
        
        self.progress = Progressbar(
            self.progress_frame, 
            orient=tk.HORIZONTAL,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X)
        
        # 操作按钮
        action_frame = Frame(self.main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = Button(
            action_frame, 
            text="开始下载", 
            command=self.start_download,
            bootstyle="success",
            width=10
        )
        self.start_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.cancel_btn = Button(
            action_frame, 
            text="取消", 
            command=self.cancel_download,
            bootstyle="warning",
            width=10,
            state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.RIGHT)
        
        # 日志显示
        log_frame = Frame(self.main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        Label(log_frame, text="操作日志:").pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=10,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 初始化变量
        self.download_thread = None
        self.cancel_flag = False
        self.driver = None
        self.path_var.set(os.path.join(os.getcwd(), 'video'))
        
        # 重定向日志到GUI
        self.redirect_logging()
    
    def redirect_logging(self):
        """重定向日志到GUI文本框"""
        class GuiLogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.config(state=tk.DISABLED)
        
        gui_handler = GuiLogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(gui_handler)
    
    def add_url(self):
        """添加单个URL到列表"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("输入错误", "URL不能为空!")
            return
            
        if not url.startswith('http'):
            messagebox.showwarning("输入错误", "请输入有效的URL!")
            return
            
        self.url_listbox.insert(tk.END, url)
        self.url_entry.delete(0, tk.END)
        logger.info(f"已添加URL: {url}")
    
    def load_url_file(self):
        """从文件加载URL列表"""
        file_path = filedialog.askopenfilename(
            title="选择URL文件",
            filetypes=[("文本文件", "*"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
                
            for url in urls:
                if url.startswith('http'):
                    self.url_listbox.insert(tk.END, url)
                    
            logger.info(f"从文件加载了 {len(urls)} 个URL")
            messagebox.showinfo("加载成功", f"成功加载 {len(urls)} 个URL")
        except Exception as e:
            logger.error(f"加载URL文件失败: {str(e)}")
            messagebox.showerror("加载失败", f"加载URL文件失败: {str(e)}")
    
    def clear_selected(self):
        """清除选中的URL"""
        selected = self.url_listbox.curselection()
        if not selected:
            return
            
        for index in selected[::-1]:
            self.url_listbox.delete(index)
    
    def clear_all(self):
        """清除所有URL"""
        if not self.url_listbox.size():
            return
            
        if messagebox.askyesno("确认", "确定要清空所有URL吗?"):
            self.url_listbox.delete(0, tk.END)
            logger.info("已清空URL列表")
    
    def browse_directory(self):
        """选择保存目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)
    
    def setup_driver(self):
        try:
            # 配置选项 - 添加更多参数减少错误日志
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--log-level=3')  
            options.add_argument('--disable-software-rasterizer')  
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])

            # 使用当前目录的chromedriver.exe
            chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
            service = Service(executable_path=chromedriver_path)
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            logger.info("浏览器驱动初始化成功")
            return driver
        except Exception as e:
            logger.error(f"浏览器初始化失败: {str(e)}")
            logger.error("请检查：")
            logger.error("1. chromedriver.exe是否在当前目录")
            logger.error("2. chromedriver.exe是否与Chrome版本匹配")
            logger.error("3. 是否已关闭所有Chrome进程")
            messagebox.showerror("浏览器错误", f"浏览器初始化失败: {str(e)}\n请检查chromedriver配置!")
            return None

    def download_video(self, video_url, filename, referer):
        """视频下载函数"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': referer,
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive'
        }

        try:
            with requests.get(video_url, headers=headers, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return True
        except Exception as e:
            logger.error(f"下载失败: {str(e)}")
            if os.path.exists(filename):
                os.remove(filename)
            return False

    def process_urls(self):
        """处理URL列表"""
        # 获取所有URL
        urls = self.url_listbox.get(0, tk.END)
        total = len(urls)
        
        if not total:
            logger.warning("没有需要下载的URL")
            messagebox.showwarning("下载错误", "没有需要下载的URL!")
            return
            
        # 创建保存目录
        video_dir = self.path_var.get()
        os.makedirs(video_dir, exist_ok=True)
        logger.info(f"视频保存目录: {video_dir}")
        
        # 初始化浏览器
        self.driver = self.setup_driver()
        if not self.driver:
            return
            
        # 更新UI状态
        self.start_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress.config(maximum=total)
        self.progress['value'] = 0
        self.cancel_flag = False
        
        # 处理每个URL
        success_count = 0
        for idx, url in enumerate(urls, 1):
            if self.cancel_flag:
                break
                
            try:
                # 更新进度
                self.progress['value'] = idx
                self.progress_label.config(text=f"处理中: {idx}/{total} - {url[:30]}...")
                logger.info(f"处理第 {idx}/{total} 个视频: {url}")
                
                # 访问页面
                self.driver.get(url)
                time.sleep(5)
                
                # 获取视频源URL
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                video_tag = soup.find('video')
                
                if not video_tag:
                    logger.warning("未找到video标签，跳过")
                    continue
                    
                sources = video_tag.find_all('source')
                if len(sources) < 2:
                    logger.warning(f"只找到 {len(sources)} 个source标签")
                    continue
                    
                video_url = sources[1].get('src')
                if not video_url:
                    logger.warning("第二个source标签无src属性")
                    continue
                    
                # 下载视频
                video_id = url.split('/')[-1] or f"video_{int(time.time())}"
                filename = os.path.join(video_dir, f"{video_id}.mp4")
                
                if self.download_video(video_url, filename, url):
                    success_count += 1
                    logger.info(f"下载成功: {filename}")
                else:
                    logger.error("下载失败")
                    
            except Exception as e:
                logger.error(f"处理出错: {str(e)}")
            
            # 间隔
            if idx < total:
                time.sleep(2)
        
        # 清理
        if self.driver:
            self.driver.quit()
            self.driver = None
            
        # 恢复UI状态
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        
        # 显示结果
        result_msg = f"完成啦！成功下载 {success_count}/{total} 个视频~"
        self.progress_label.config(text=result_msg)
        logger.info(result_msg)
        
        if not self.cancel_flag:
            messagebox.showinfo("下载完成", result_msg)
    
    def start_download(self):
        """开始下载线程"""
        if not self.url_listbox.size():
            messagebox.showwarning("下载错误", "没有需要下载的URL!")
            return
            
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showwarning("操作错误", "下载任务正在进行中!")
            return
            
        # 检查chromedriver
        if not os.path.exists("chromedriver.exe"):
            messagebox.showerror("文件缺失", "缺少chromedriver.exe文件!\n请下载匹配版本的chromedriver.exe放到当前目录")
            return
            
        # 创建并启动下载线程
        self.download_thread = threading.Thread(target=self.process_urls, daemon=True)
        self.download_thread.start()
    
    def cancel_download(self):
        """取消下载"""
        if messagebox.askyesno("确认", "确定要取消下载吗?"):
            self.cancel_flag = True
            self.cancel_btn.config(state=tk.DISABLED)
            logger.info("用户取消了下载操作")

if __name__ == "__main__":
    root = tk.Tk()
    app = DouyinDownloaderApp(root)
    root.mainloop()
