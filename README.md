# MKV 文件处理工具

一个功能强大的 MKV 文件处理工具，支持文件合并、字体管理和字幕处理等功能。

## 功能特性

- 🎬 MKV 文件合并
- 📝 字幕处理
- 🖼️ 字体管理
- 📊 文件信息查看
- 🎨 图形用户界面
- 📋 详细的日志记录

## 系统要求

- Python 3.8 或更高版本
- 操作系统：Windows/macOS/Linux

## 安装

1. 克隆仓库：
```bash
git clone [您的仓库地址]
cd mkvmerge
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 图形界面

运行以下命令启动图形界面：
```bash
python main.py
```

### 命令行

主要功能模块：
- `MKVInfo.py`: MKV 文件信息查看
- `MergeMkv.py`: MKV 文件合并
- `FontManager.py`: 字体管理
- `Verification.py`: 文件验证

## 项目结构

```
├── main.py              # 程序入口
├── MKVInfo.py          # MKV 文件信息处理
├── MKVTrack.py         # MKV 轨道处理
├── MkvFile.py          # MKV 文件基础操作
├── MergeMkv.py         # MKV 合并功能
├── MergeMkvGUI.py      # 合并功能图形界面
├── FontManager.py      # 字体管理
├── FontInfo.py         # 字体信息处理
├── FontScanWindow.py   # 字体扫描界面
├── LogManager.py       # 日志管理
├── LogFormatter.py     # 日志格式化
└── requirements.txt    # 项目依赖
```

## 依赖项

- PyQt6: GUI 界面
- pymkv: MKV 文件处理
- fontTools: 字体处理
- pysubs2: 字幕处理
- rich & coloredlogs: 日志美化
- pyinstaller: 打包工具

## 许可证

[待定]

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

[待补充] 