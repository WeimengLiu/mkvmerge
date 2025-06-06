#!/usr/bin/python3
import sys
import os
import platform
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from LogManager import LogManager
from utils import get_resource_path  # 从 utils 导入

def main():
    # 在 macOS 上设置环境变量以抑制 IMK 警告
    if platform.system() == 'Darwin':
        os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
        # 禁用 IMK 日志
        os.environ['IMK_LOG_LEVEL'] = '0'
    
    # 初始化日志系统
    logger = LogManager.get_logger()
    
    # 确保日志目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 设置应用程序图标
    icon_path = get_resource_path('icon.ico')
    
    # Windows 特定的应用程序 ID 设置
    if platform.system() == 'Windows':
        try:
            import ctypes
            myappid = 'com.mkvmerge.gui'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            logger.warning(f"设置 Windows 应用程序 ID 失败: {str(e)}")
    
    # 启动GUI应用
    app = QApplication(sys.argv)
    
    # 设置应用程序图标
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # 在这里导入主窗口类
    from MergeMkvGUI import MergeMkvWindow
    window = MergeMkvWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 