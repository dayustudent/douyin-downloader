# 🎬 抖音无水印视频下载器 | Douyin No-Watermark Downloader 🚀

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/ChromeDriver-Compatible-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-Apache%202.0-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Platform-Windows-blueviolet?style=for-the-badge" />
</p>

> 🌟 一个简单、安全、高效的抖音无水印视频下载工具，支持 GUI 与便携命令行双模式，基于 Python + Selenium 自动化实现，开源、透明、无风险！

---

## 🌈 功能亮点 ✨

- ✅ **无水印下载**：自动去除抖音视频水印，高清保存本地！
- 🖱️ **GUI 图形界面**：支持可安装版本，小白也能轻松上手！
- 💼 **便携版本**：无需安装，绿色运行，支持 UI 与无 UI 模式
- 🔗 **支持链接格式**：`https://www.douyin.com/video/xxxxxxxxxxxxxxxx`
- 🛠️ **自动化浏览器**：使用 Chrome 浏览器模拟真实访问，稳定抓取
- 🔐 **安全透明**：不收集用户数据，使用本地浏览器，无安全风险
- 📦 **开源自由**：Apache-2.0 协议，欢迎 Fork、Star 与贡献！

---

## 🖥️ 支持平台

- ✅ **Windows**（当前仅支持）
- 🚫 macOS / Linux（开发中，敬请期待）

---

## 📦 版本说明

| 版本类型 | 说明 | 下载地址 |
|--------|------|---------|
| 🧩 **可安装版（UI）** | 带图形界面，一键安装，自动配置 Chromedriver | [👉 点击下载 Installer](https://github.com/dayustudent/douyin-downloader/releases/download/v1.0.0/UI-Installer-DouyinDownloader.exe) |
| 🧳 **便携版 - UI** | 无需安装，解压即用，带图形界面 | [👉 点击下载 UI 版](https://github.com/dayustudent/douyin-downloader/releases/download/v1.0.0/UI-DouyinDownloader.exe) |
| 🖥️ **便携版 - CLI** | 无界面，命令行运行，轻量高效 | [👉 点击下载 CLI 版](https://github.com/dayustudent/douyin-downloader/releases/download/v1.0.0/DouyinDownloader.exe) |

---

## ⚙️ 环境准备（便携版必看！）

本项目依赖 **ChromeDriver** 来驱动浏览器自动化，需根据你的 Google Chrome 版本手动下载并配置。

### 📥 安装对应的库 
*(非执行 python 代码，使用 exe 程序可省略此步）*
> `cmd` / `powershell` `cd` 到程序目录 
```bash
pip install -r requirements.txt
```

### 🔍 查看 Chrome 版本
- `方法1` 打开 Chrome 浏览器 → 右上角 `...` → 帮助 → 关于 Google Chrome
- `方法2` 打开 Chrome 浏览器 → 地址栏输入`chrome://version/`

---

### 📥 下载 ChromeDriver（直接替换 `<chrome-version>`）

根据你的 Chrome 主版本号选择对应链接：

| Chrome 版本 | 下载地址模板 |
|------------|-------------|
| **Chrome < 115** | `https://chromedriver.storage.googleapis.com/<chrome-version>/chromedriver_win32.zip` |
| **Chrome ≥ 115** | `https://storage.googleapis.com/chrome-for-testing-public/<chrome-version>/win32/chromedriver-win32.zip` |

📌 **示例**（如果你的 Chrome 版本是 `131.0.6778.85`）：
```
https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.85/win32/chromedriver-win32.zip
```

> 💡 小贴士：只需复制链接并把 `<chrome-version>` 替换为你的完整版本号即可！

---

### 📁 配置步骤

1. 下载对应版本的 `chromedriver_win32.zip`
2. 解压得到 `chromedriver.exe`
3. 将其放入程序同级目录（与 `.exe` 文件放在一起）
4. 运行即可！

✅ 示例目录结构（便携版）：
```
douyin-downloader/
├── chromedriver.exe        ← 放在这里！
├── UI-DouyinDownloader.exe ← 双击运行
└── video/                  ← 视频默认保存在此
```

---

## 🚀 快速开始（无需编程基础）

### 🧩 使用可安装版（推荐新手）

1. 下载安装程序：[UI-Installer-DouyinDownloader.exe](https://github.com/dayustudent/douyin-downloader/releases/download/v1.0.0/UI-Installer-DouyinDownloader.exe)
2. 双击运行，按提示选择安装路径
3. 安装程序会**自动引导你下载 Chromedriver**
4. 安装完成后创建桌面快捷方式，一键启动！

> ✅ 安装器功能：自动检测 Chrome 版本 → 引导下载 → 解压配置 → 创建快捷方式

---

### 🧳 使用便携版（绿色免安装）

#### 方式一：带界面（推荐普通用户）
1. 下载：[UI-DouyinDownloader.exe](https://github.com/dayustudent/douyin-downloader/releases/download/v1.0.0/UI-DouyinDownloader.exe)
2. 下载对应版本的 `chromedriver.exe` 并放入同目录
3. 双击运行，输入链接即可下载

#### 方式二：命令行版（适合高级用户）*（该功能测试中）*
1. 下载：[DouyinDownloader.exe](https://github.com/dayustudent/douyin-downloader/releases/download/v1.0.0/DouyinDownloader.exe)
2. 打开 CMD，运行：
```bash
DouyinDownloader.exe --url "https://www.douyin.com/video/1234567890123456789"
```

---

## 📥 下载示例

输入链接：
```
https://www.douyin.com/video/7891234560123456789
```

✅ 自动识别 → 播放页面 → 抓取无水印源 → 保存至 `video/` 目录！

📁 你可以在界面中自定义保存路径，支持批量下载多个视频！

---

## 🛡️ 安全声明

- ❌ 不收集任何用户隐私
- 🔒 所有操作在本地处理，仅使用浏览器抖音网页服务
- 🌐 使用你自己的浏览器会话，无账号泄露风险
- 🧹 程序干净透明，开源可审计

> 我们尊重平台规则，本工具仅用于个人学习与研究，请勿用于商业或大规模爬取。

---

## 📄 开源协议

本项目采用 **Apache License 2.0** 开源协议，自由使用、修改、分发，但请保留原始版权信息。

👉 [LICENSE](LICENSE)

---

## 🌟 支持我们

如果你喜欢这个项目，欢迎：

- ⭐ **Star** 项目，让更多人看到！
- 🐞 **提交 Issue** 报告 Bug 或提出建议
- 🤝 **Pull Request** 参与开发，支持更多功能（如 macOS 支持、批量下载等）

---

## 📬 联系方式

- GitHub: [@dayustudent](https://github.com/dayustudent)
- Gitee : [@dayustudent](https://gitee.com/dayustudent)
- 邮箱：dayutx@126.com

---

> 🎉 感谢使用！让下载抖音视频变得更简单、更自由！  
> —— 由 Python 驱动，为效率而生 💻❤️
