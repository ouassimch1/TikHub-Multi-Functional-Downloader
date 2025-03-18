# TikHub-Multi-Functional Downloader 🚀📱

<p align="center">
  <b>English</b> | <a href="README-zh.md">简体中文</a>
</p>

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/TikHub/TikHub-Multi-Functional-Downloader/releases)
[![Python](https://img.shields.io/badge/python-3.9+-yellow)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/TikHub/TikHub-Multi-Functional-Downloader.svg?style=social&label=Stars)](https://github.com/TikHub/TikHub-Multi-Functional-Downloader)
[![GitHub forks](https://img.shields.io/github/forks/TikHub/TikHub-Multi-Functional-Downloader.svg?style=social&label=Forks)](https://github.com/TikHub/TikHub-Multi-Functional-Downloader)
[![GitHub issues](https://img.shields.io/github/issues/TikHub/TikHub-Multi-Functional-Downloader.svg)](https://github.com/TikHub/TikHub-Multi-Functional-Downloader/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/TikHub/TikHub-Multi-Functional-Downloader/pulls)
[![License](https://img.shields.io/github/license/TikHub/TikHub-Multi-Functional-Downloader.svg)](https://github.com/TikHub/TikHub-Multi-Functional-Downloader/blob/main/LICENSE)
[![Made with ❤️](https://img.shields.io/badge/made%20with-%E2%9D%A4%EF%B8%8F-red)](https://github.com/Evil0ctal)

A powerful cross-platform video download GUI application that supports multiple platforms including [TikTok](https://www.tiktok.com/), [Douyin](https://www.douyin.com/), and others. Built on the [TikHub.io](https://tikhub.io/) API for watermark-free video downloading.

## 📋 Table of Contents

- [🌟 Features](#-features)
- [🖥️ System Requirements](#️-system-requirements)
- [🚀 Installation and Running](#-installation-and-running)
- [🔑 API Key Setup](#-api-key-setup)
- [📖 User Guide](#-user-guide)
- [📸 Application Screenshots](#-application-screenshots)
- [❓ FAQ](#-faq)
- [🤝 Contribution Guidelines](#-contribution-guidelines)
- [📄 License](#-license)
- [🎉 Acknowledgments](#-acknowledgments)

## 🌟 Features

- 📹 **Multi-platform Seamless Support**:
  - ✨ **TikTok Video Download**: Support for watermark-free downloading of various TikTok videos, image collections, and music
  - ✨ **Douyin Video Download**: Perfect support for Douyin platform videos, image collections, and music works
  - 🔄 **Automatic Platform Detection**: Intelligently detect link types and automatically select the appropriate download method
  
- 📥 **Diverse Download Options**:
  - 🔗 **Single Video Download**: Quickly download individual videos without watermarks via share links
  - 👤 **User Video Batch Download**: One-click access to all public videos from a specified user
  - 📋 **Batch Link Processing**: Support for batch downloading of mixed platform links
  - 🖼️ **Image Collection Support**: Complete saving of multi-image works, including metadata
  
- 🛠️ **Advanced Features**:
  - 🧠 **Smart Parsing**: Automatically processes short links, redirect links, and various link formats
  - 🔍 **Media Preview**: View video thumbnails, user information, and detailed data before downloading
  - 🎵 **Audio Extraction**: Option to download only the audio portion of videos
  - 📊 **Download Management**: Real-time display of download progress, speed, and status
  
- ⚙️ **User-Friendly Settings**:
  - 🌓 **Theme Switching**: Support for light, dark, and system-following modes
  - 🌍 **Multi-language Support**: Built-in Chinese and English interfaces, with support for community language extensions
  - 📁 **Custom Storage Path**: Flexible setting of download file save locations
  - 🔄 **Automatic Update Checking**: Keep software always up to date

- 🔐 **Security and Compliance**:
  - 🛡️ **Safe Downloads**: Contains no ads or malicious code
  - ⚖️ **Compliant Usage**: Designed for downloading publicly available content that users have the right to access
  - 🔒 **Privacy Protection**: Doesn't collect personal data, protects user privacy

## 🖥️ System Requirements

### 💻 Supported Platforms
- 🪟 Windows 7/10/11 (Best Support)
- 🍎 macOS 10.14+ (Intel & M1/M2)
- 🐧 Linux (Ubuntu, Debian, Fedora, etc.)
- 🌐 Other operating systems that support Python 3.9+

### 🔧 Technical Requirements
- 🐍 Python 3.9 or higher
- 📦 Required Python dependencies (see `requirements.txt`)
- 🔑 TikHub.io API key ([Get for free](https://user.tikhub.io/))
- 🌐 Stable network connection (Proxy tools recommended for users in mainland China downloading TikTok videos)

## 🚀 Installation and Running

### 📥 Download Methods

#### 1. Windows Users (Recommended) 💯
- ⬇️ Download pre-compiled `.exe` executable directly from [Releases](https://github.com/TikHub/TikHub-Multi-Functional-Downloader/releases)
- 📦 No need to install Python environment, ready to use out of the box
- 🖱️ Double-click to run the application

#### 2. Other Platforms/Source Code Installation 🧩

##### Method One: Run Source Code Directly 👨‍💻
1. Clone the repository
```bash
git clone https://github.com/TikHub/TikHub-Multi-Functional-Downloader.git
cd TikHub-Multi-Functional-Downloader
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python main.py
```

##### Method Two: Package using build.py 📦
1. Clone the repository and enter the directory
```bash
git clone https://github.com/TikHub/TikHub-Multi-Functional-Downloader.git
cd TikHub-Multi-Functional-Downloader
```

2. Install packaging dependencies and execute packaging
```bash
pip install -r requirements.txt
python build.py
```
- ✅ Will automatically generate executable files according to your operating system
- 📁 Generated files are located in the `./dist` directory

## 🔑 API Key Setup

Using the TikHub downloader requires obtaining an API key from [TikHub.io](https://user.tikhub.io/) (completely free):

1. 🔐 Register an account on [TikHub.io](https://user.tikhub.io/) (email only required)
2. 📆 Log into the user dashboard, click the `Check-in` button at the top of the page to receive daily check-in rewards
    - **Note**: Check-in rewards affect download count, can be claimed once every 24 hours
    - **Note**: If you don't check in, you may not be able to download videos
3. 📊 Enter the user dashboard, click `API Management/Pricing` on the left, then create your exclusive API key
4. ⚙️ Click to select all `API Key Scopes`, ensure all permissions are selected and granted to the API key, then click save
5. 💡 Enter the API key in the `Settings` tab of the application, click the `Save` button
   - **Note**: The API key only needs to be set up once, it will be automatically saved in the local configuration file
   - **Note**: If you encounter any problems during use, please check if your API key is correct
   - **Note**: If you need a higher download count, consider purchasing an API package

## 📖 User Guide

### 🎬 Single Video Download
1. 📋 Copy the video sharing link from Douyin/TikTok app, examples:
    - Douyin: https://v.douyin.com/i5WdL2Ls/
    - TikTok: https://www.tiktok.com/@minecraft/video/7439081942194212138
2. 📲 Paste the video URL in the "Video Download" tab
3. 🔍 Click "Parse Video" to get video information
4. 👁️ View video preview and detailed information
5. 💾 Click "Download Video" to save to local storage

### 👤 User Video Download
1. 🔗 Copy the user homepage URL, examples:
   - Douyin: https://www.douyin.com/user/MS4wLjABAAAAoctrW5qzQp6h2H32mRKenXU_0-cmgjgOxIc768mlwjqKVjQbFdD1NeEzi2TMbGM0
   - TikTok: https://www.tiktok.com/@minecraft
2. 📲 Paste the user homepage URL in the "User Videos" tab
3. 🔍 Click "Get User Info"
   - Displays user avatar, nickname, followers count, etc.
   - This step will trigger one API call
4. 📊 Set the number of videos to fetch (maximum depends on user's work count)
   - Default gets the user's latest 20 videos
   - Every additional 20 videos will trigger one API call
5. ✅ Select videos to download, or use "Download All Videos"
6. 📥 Wait for the download queue to complete

### 📚 Batch Download
1. 📋 Prepare multiple video URLs (one per line)
2. 📲 Paste these URLs in the "Batch Download" tab
3. 🔍 Click "Extract Links" to verify the number of downloadable links
   - Supports mixed platform links, short links, and redirect links or share text
4. 📥 Click "Start Batch Download"
   - Successful links will trigger one API call
5. 📊 View download progress and status
6. ✅ After all downloads are complete, success/failure statistics will be displayed

### ⚙️ Advanced Settings
1. 📁 Customize download folder path, automatically skip existing files (avoid duplicate downloads)
2. 🎛️ Adjust concurrent download count
3. 🌓 Choose interface theme (light/dark/follow system)
4. 🌍 Switch interface language
5. 🔄 Set automatic update check frequency

## 📸 Application Screenshots

### 1. Single Work Download Page 🎬
![Single Video Download](screenshots/single_video_download.png)
- 🔗 Supports Douyin and TikTok links as input
- 👁️ Can directly preview video details
- 📊 Displays likes count, comments count, and other data
- 📥 One-click download function

### 2. User Homepage Download Page 👤
![User Video Download](screenshots/user_video_download.png)
- 🔍 Supports Douyin and TikTok user homepage links
- ⚙️ Can set maximum video count
- 📊 Displays user profile and work statistics
- ✅ Batch selection for download

### 3. Batch Download Page 📚
![Batch Download](screenshots/batch_download.png)
- 🔄 Supports mixed platform links
- 🧠 One-click extraction of links from input text
- 📁 Supports importing links from text files
- ⚡ Parallel downloads for improved efficiency

### 4. Settings Page ⚙️
![Settings Page](screenshots/settings_page.png)
- 🌓 Supports theme switching (light, dark, system)
- 🌍 Multi-language support (Chinese, English)
- 🔌 Community contributed language pack interface
- 🔄 Check for updates function

### 5. Image Collection Preview - HTML Preview 🖼️
![Image Collection Preview](screenshots/image_preview.png)
- 🌐 Automatically generates HTML file
- 📱 Responsive design, suitable for various devices
- 🖼️ Supports image collection and album preview
- 👆 User-friendly image browsing interface

### 6. Image Collection Details Preview 📊
![Image Collection Details](screenshots/image_details.png)
- 📝 View image collection detailed information
- 🌐 Supports multi-platform image collection preview
- ⏱️ Displays image collection creation time and related metadata
- 💾 One-click save of original resolution images

## ❓ FAQ

### 🔄 API Usage Related Issues

#### Q: Why did my API request fail?
A: Possible reasons:
- ⏰ You've used up your API call count for today. Daily check-in can get free quota
- 🔑 API key is not correctly configured or has expired. Please check settings and ensure it's saved
- 🌐 Network issues prevent connection to TikHub servers

#### Q: How can I increase my API call limit?
A: There are several ways:
1. 📆 Log in to [TikHub.io](https://user.tikhub.io/) daily for check-in to get free quota
2. 💰 Purchase a higher-level API package to get more call counts and higher concurrency limits
3. 📊 Plan download tasks reasonably, avoid unnecessary API calls

### 📥 Download Related Issues

#### Q: Why can't a video be downloaded or parsing fails?
A: Possible reasons:
- 🔒 The video may be set to private and cannot be publicly accessed
- 🌐 Users in mainland China need to use a proxy tool to download TikTok videos
- 🔗 Link format is incorrect or has expired

#### Q: How to download high-definition videos?
A: This software downloads the highest quality version by default. If you encounter problems:
- 🎥 Original video quality is limited by the original upload quality
- 📱 Some platforms may limit high-definition video downloads

### ⚙️ Software Usage Issues

#### Q: What if the software fails to start?
A: Try the following methods:
1. 🔄 Download the latest version of the software again
2. 📦 Windows users try installing [Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
3. 📝 Check the log file (located in the `app.log` file in the application directory) and contact the developer

#### Q: How to backup my settings and API key?
A: Configuration file is located at:
    - `.\TikHub-Multi-Functional-Downloader\config.json`

Backing up this file will save all your settings and API key.

## 🤝 Contribution Guidelines

We welcome all forms of contribution, whether feature requests, bug reports, or code contributions!

### 📝 How to Contribute

1. 🍴 Fork this repository
2. 🌿 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔄 Submit a Pull Request

### 🌍 Language Contributions
- You can contribute translations by adding new language files
- Language files are located in the `./downloader/locales` directory
- Please use ISO language codes as filenames (e.g.: `en.json`, `zh.json`)

### 🐛 Reporting Issues
- Use GitHub Issues to report problems
- Please provide detailed reproduction steps and environment information
- Attaching relevant logs and screenshots is helpful

## 📄 License

This project is licensed under the GNU General Public License (GNU GPL) Version 3.

### GNU General Public License (GPL) 📜

Version 3, June 29, 2007

 Copyright (C) 2007 Free Software Foundation <https://fsf.org/>

 Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.

#### Main Terms:

- 🆓 Free Use: Anyone can use this software for any purpose
- 🔄 Free Distribution: You can freely copy and distribute this software
- 🛠️ Free Modification: You can modify the source code to meet your needs
- 📖 Source Code Must Be Open: Any modified version of this software must also be open-sourced under the GPL license

For complete license details, please check the [LICENSE](https://github.com/TikHub/TikHub-Multi-Functional-Downloader/blob/main/LICENSE) file.

## 🎉 Acknowledgments

### 👨‍💻 Developers
- [@Evil0ctal](https://github.com/Evil0ctal) - Core development and maintenance

### 🌐 Resources
- [TikHub.io](https://tikhub.io) - Provides powerful API support
- [Python](https://python.org) - Main development language
- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap/) - GUI framework

### 📶 Support

- [🏠 Home](https://tikhub.io/) - TikHub homepage
- [👨‍💻GitHub](https://github.com/TikHub) - TikHub GitHub homepage
- [📧 Discord](https://discord.gg/aMEAS8Xsvz) - TikHub community
- [⚡ Documents (Swagger UI)](https://api.tikhub.io/) - API documentation
- [🦊 Documents (Apifox UI)](https://docs.tikhub.io/) - API documentation

### 🙏 Special Thanks
- Thanks to all developers and users who help improve the project through issue reports, feature suggestions, and code contributions
- Thanks to the open source community for providing various tools and libraries
- Thanks to all translators who contributed to multi-language support

---

**📢 Notes**:
1. ⚖️ Please comply with the copyright and usage policies of each platform, only download publicly available content that you have the right to access
2. 📝 According to the GNU GPL v3 license, any modifications or derivative works based on this project must also follow GPL v3 and open source the code
3. 🚫 This tool should not be used to infringe on others' intellectual property rights or violate terms of service
4. 🔄 Regularly check for updates to get the latest features and security fixes