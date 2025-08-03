import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse

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

class DouyinDownloaderCLI:
    def __init__(self):
        # 初始化变量
        self.driver = None
        self.cancel_flag = False
        self.save_path = os.path.join(os.getcwd(), 'video')
        
        # 确保保存目录存在
        os.makedirs(self.save_path, exist_ok=True)
        logger.info(f"视频将保存到: {self.save_path}")
    
    def setup_driver(self):
        """初始化浏览器驱动"""
        try:
            # 配置选项
            options = Options()
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

    def process_urls(self, urls):
        """处理URL列表"""
        total = len(urls)
        
        if not total:
            logger.warning("没有需要下载的URL")
            return
            
        # 初始化浏览器
        self.driver = self.setup_driver()
        if not self.driver:
            return False
            
        self.cancel_flag = False
        success_count = 0
        
        # 处理每个URL
        for idx, url in enumerate(urls, 1):
            if self.cancel_flag:
                break
                
            try:
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
                filename = os.path.join(self.save_path, f"{video_id}.mp4")
                
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
            
        # 显示结果
        result_msg = f"完成！成功下载 {success_count}/{total} 个视频"
        logger.info(result_msg)
        return success_count

    def set_save_path(self, path):
        """设置保存路径"""
        self.save_path = path
        os.makedirs(self.save_path, exist_ok=True)
        logger.info(f"视频保存路径已更新为: {self.save_path}")

    def cancel(self):
        """取消下载"""
        self.cancel_flag = True
        logger.info("下载操作已取消")

def main():
    print("抖音视频下载器 - 命令行版本")
    print("=" * 40)
    
    downloader = DouyinDownloaderCLI()
    
    # 检查chromedriver
    if not os.path.exists("chromedriver.exe"):
        logger.error("缺少chromedriver.exe文件！请下载匹配版本的chromedriver.exe放到当前目录")
        return
    
    # 获取URL来源
    print("\n请选择URL来源:")
    print("1. 手动输入URL")
    print("2. 从文本文件读取URL")
    choice = input("请输入选项(1/2): ").strip()
    
    urls = []
    if choice == "1":
        print("\n请输入抖音视频URL(输入空行结束):")
        while True:
            url = input("URL: ").strip()
            if not url:
                break
            if url.startswith('http'):
                urls.append(url)
                print(f"已添加URL: {url}")
            else:
                print("无效的URL，必须以http或https开头")
    elif choice == "2":
        file_path = input("\n请输入包含URL的文本文件路径: ").strip()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and line.startswith('http')]
            print(f"从文件加载了 {len(urls)} 个URL")
        except Exception as e:
            logger.error(f"加载URL文件失败: {str(e)}")
            return
    else:
        print("无效的选项")
        return
    
    if not urls:
        print("没有有效的URL，程序退出")
        return
    
    # 设置保存路径
    custom_path = input("\n请输入保存路径(留空使用默认路径): ").strip()
    if custom_path:
        downloader.set_save_path(custom_path)
    
    # 开始下载
    print("\n开始下载...")
    start_time = time.time()
    success_count = downloader.process_urls(urls)
    elapsed_time = time.time() - start_time
    
    print("\n下载结果:")
    print(f"总URL数: {len(urls)}")
    print(f"成功下载: {success_count}")
    print(f"失败: {len(urls) - success_count}")
    print(f"耗时: {elapsed_time:.2f}秒")
    
    # 等待用户退出
    input("\n按任意键退出...")

if __name__ == "__main__":
    main()
