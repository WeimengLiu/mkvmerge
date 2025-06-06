from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLineEdit, QLabel, QTextEdit, 
                           QFileDialog, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
import os
from FontManager import FontManager

class FontScanWorker(QThread):
    progress = pyqtSignal(int, int)
    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, font_dir, font_manager):
        super().__init__()
        self.font_dir = font_dir
        self.font_manager = font_manager
        
        # 创建一个函数来处理日志输出
        def log_handler(message):
            # 发送处理相关的信息到GUI
            if any(x in message for x in [
                "处理字体文件:", 
                "找到字体名称:", 
                "处理失败:",
                "处理超时:"
            ]):
                self.log.emit(message)
            # 保持原始的logger.info调用
            self.font_manager.logger.info(message)
        
        # 替换FontManager的log方法
        self.font_manager.log = log_handler
        self._is_running = True

    def stop(self):
        """停止扫描"""
        self._is_running = False
        self.wait()  # 等待线程结束

    def run(self):
        try:
            self.font_manager.scan_font_directory(
                self.font_dir,
                callback=lambda current, total: self.progress.emit(current, total)
            )
            if self._is_running:
                self.finished.emit()
        except Exception as e:
            self.log.emit(f'错误: {str(e)}')
            import traceback
            self.log.emit(traceback.format_exc())

class FontScanWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.font_manager = FontManager()
        self.worker = None
        self.initUI()

    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, '确认', '正在扫描字体，确定要关闭窗口吗？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_scan()
                self.worker.wait()  # 等待线程结束
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def stop_scan(self):
        """停止扫描"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.scan_btn.setEnabled(True)
            self.log_text.append('扫描已取消')

    def initUI(self):
        """初始化UI"""
        self.setWindowTitle('字体扫描工具')
        self.setGeometry(100, 100, 600, 400)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 显示数据库路径
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel('数据库路径:'))
        
        # 创建只读的输入框显示数据库路径
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setReadOnly(True)
        self.db_path_edit.setText(self.font_manager.db_path)
        self.db_path_edit.setStyleSheet('''
            QLineEdit {
                border: none;
                background: transparent;
                color: #666666;
            }
        ''')
        db_layout.addWidget(self.db_path_edit)
        layout.addLayout(db_layout)
        
        # 字体目录选择
        font_layout = QHBoxLayout()
        self.font_edit = QLineEdit()
        font_btn = QPushButton('选择字体目录')
        font_btn.clicked.connect(self.select_font_dir)
        font_layout.addWidget(QLabel('字体目录:'))
        font_layout.addWidget(self.font_edit)
        font_layout.addWidget(font_btn)
        layout.addLayout(font_layout)
        
        # 进度条
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel('0/0')
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setAcceptRichText(True)  # 允许富文本
        layout.addWidget(self.log_text)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.scan_btn = QPushButton('开始扫描')
        self.scan_btn.clicked.connect(self.start_scan)
        self.cancel_btn = QPushButton('取消扫描')
        self.cancel_btn.clicked.connect(self.stop_scan)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def select_font_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, '选择字体目录')
        if dir_path:
            self.font_edit.setText(dir_path)

    def start_scan(self):
        font_dir = self.font_edit.text()

        if not font_dir:
            self.log_text.append('请选择字体目录！')
            return

        if not os.path.exists(font_dir):
            self.log_text.append('错误：字体目录不存在！')
            return

        self.scan_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)

        self.worker = FontScanWorker(font_dir, self.font_manager)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.log_text.append)
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.start()

    def update_progress(self, current: int, total: int):
        """更新进度显示"""
        percentage = int(current / total * 100) if total > 0 else 0
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(f'{current}/{total}')

    def on_scan_finished(self):
        self.scan_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.log_text.append(f'扫描完成！数据库保存在：{self.font_manager.db_path}') 