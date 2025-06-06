#!/usr/bin/python3
import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from LogManager import LogManager
from utils import get_resource_path  # 从 utils 导入

def main():
    # 初始化日志系统
    logger = LogManager.get_logger()
    
    # 确保日志目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 设置应用程序图标
    icon_path = get_resource_path('icon.ico')
    if os.path.exists(icon_path):
        myappid = 'com.mkvmerge.gui'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    # 启动GUI应用
    app = QApplication(sys.argv)
    
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