#!/usr/bin/python3
import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTextEdit, QFileDialog,
    QProgressBar, QCheckBox, QMessageBox
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QMetaObject, Q_ARG,
    pyqtSlot, QObject
)
from PyQt6.QtGui import QIcon, QTextCursor
import logging
from LogManager import LogManager
import subprocess
from FontScanWindow import FontScanWindow
from MergeMkv import process_mkv_files


class LogSignalEmitter(QObject):
    """用于发送日志信号的类"""
    log_signal = pyqtSignal(str)

class CustomHandler(logging.Handler):
    """自定义日志处理器，将日志输出重定向到GUI"""
    def __init__(self, callback):
        super().__init__()
        self.setFormatter(logging.Formatter('%(message)s'))
        self.signal_emitter = LogSignalEmitter()
        self.signal_emitter.log_signal.connect(callback)
        
    def emit(self, record):
        msg = self.format(record)
        # 如果消息已经包含HTML标签，直接使用
        if '<font color=' in msg:
            formatted_msg = msg
        else:
            # 根据日志级别设置颜色
            if record.levelno >= logging.ERROR:
                formatted_msg = f'<font color="red">{msg}</font>'
            else:
                formatted_msg = msg
                
        # 使用信号发送消息
        self.signal_emitter.log_signal.emit(formatted_msg)

class MergeWorker(QThread):
    """MKV合并工作线程"""
    log = pyqtSignal(str)
    finished = pyqtSignal()
    process_created = pyqtSignal(object)

    def __init__(self, input_dir: str, output_dir: str, execute: bool = True):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.execute = execute
        self._is_running = True
        self.process = None

    def run(self):
        try:
            # 设置进程创建回调
            def on_process_created(p):
                self.process = p
                self.process_created.emit(p)
            
            process_mkv_files.process_created_callback = on_process_created
            
            process_mkv_files(
                directory=self.input_dir,
                output=self.output_dir,
                execute=self.execute,
                print_command=True
            )
            
            if self._is_running:
                self.finished.emit()
                
        except Exception as e:
            self.log.emit(f'Error: {str(e)}')
            import traceback
            self.log.emit(traceback.format_exc())
        finally:
            # 清除回调
            if hasattr(process_mkv_files, 'process_created_callback'):
                del process_mkv_files.process_created_callback

    def stop(self):
        """停止工作线程"""
        self._is_running = False
        
        # 设置停止标志
        process_mkv_files.should_stop = True
        
        # 终止当前进程
        if self.process and self.process.poll() is None:
            try:
                if sys.platform == 'win32':
                    # 创建 startupinfo 对象
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    subprocess.run(
                        ['taskkill', '/F', '/T', '/PID', str(self.process.pid)],
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0,
                        check=True,
                        capture_output=True
                    )
                else:
                    self.process.kill()
                self.process.wait(timeout=5)
            except Exception:
                pass

class MergeMkvWindow(QMainWindow):
    """MKV合并工具主窗口"""
    def __init__(self):
        super().__init__()
        self.worker = None
        self.process = None  # 保存当前进程
        self.initUI()
        
        # 只在这里添加一次日志处理器
        logger = LogManager.get_logger()
        logger.addHandler(CustomHandler(self.append_log))

    def initUI(self):
        """初始化UI"""
        self.setWindowTitle('MKV合并工具')
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 输入目录选择
        layout.addLayout(self._create_dir_select_layout(
            '输入目录:', 
            self._create_line_edit('input_edit'),
            '选择输入目录',
            self.select_input_dir
        ))

        # 输出目录选择
        layout.addLayout(self._create_dir_select_layout(
            '输出目录:', 
            self._create_line_edit('output_edit'),
            '选择输出目录',
            self.select_output_dir
        ))

        # 字体数据库显示
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel('字体数据库:'))
        
        # 创建只读的输入框显示数据库路径
        self.font_path_edit = QLineEdit()
        self.font_path_edit.setReadOnly(True)  # 设置为只读
        self.font_path_edit.setText('fonts.db')  # 直接显示相对路径
        # 设置适当的样式，让它看起来像标签但可以选择文本
        self.font_path_edit.setStyleSheet('''
            QLineEdit {
                border: none;
                background: transparent;
                color: #666666;
            }
        ''')
        font_layout.addWidget(self.font_path_edit)
        
        # 添加字体扫描按钮
        scan_btn = QPushButton('字体扫描工具')
        scan_btn.clicked.connect(self.open_font_scan)
        font_layout.addWidget(scan_btn)
        
        layout.addLayout(font_layout)

        # 选项设置
        options_layout = QHBoxLayout()
        self.execute_checkbox = QCheckBox('执行命令')
        self.execute_checkbox.setChecked(True)
        self.execute_checkbox.setToolTip('取消选中将只生成命令而不执行')
        options_layout.addWidget(self.execute_checkbox)
        layout.addLayout(options_layout)

        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # 初始时隐藏
        layout.addWidget(self.progress_bar)
        
        # 日志显示
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setAcceptRichText(True)
        layout.addWidget(self.log_text)

        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 开始按钮
        self.start_btn = QPushButton('开始合并')
        self.start_btn.clicked.connect(self.start_merge)
        button_layout.addWidget(self.start_btn)
        
        # 停止按钮
        self.stop_btn = QPushButton('停止合并')
        self.stop_btn.clicked.connect(self.stop_merge)
        self.stop_btn.setEnabled(False)  # 初始时禁用
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)

    def _create_line_edit(self, name: str) -> QLineEdit:
        """创建并保存LineEdit控件"""
        line_edit = QLineEdit()
        setattr(self, name, line_edit)
        return line_edit

    def _create_dir_select_layout(self, label: str, line_edit: QLineEdit, 
                                btn_text: str, btn_slot) -> QHBoxLayout:
        """创建目录选择布局"""
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addWidget(line_edit)
        btn = QPushButton(btn_text)
        btn.clicked.connect(btn_slot)
        layout.addWidget(btn)
        return layout

    def select_input_dir(self):
        """选择输入目录"""
        dir_path = QFileDialog.getExistingDirectory(self, '选择输入目录')
        if dir_path:
            self.input_edit.setText(dir_path)

    def select_output_dir(self):
        """选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, '选择输出目录')
        if dir_path:
            self.output_edit.setText(dir_path)

    def select_font_dir(self):
        """选择字体数据库"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择字体数据库', '', 'SQLite数据库 (*.db)')
        if file_path:
            self.font_edit.setText(file_path)

    def open_font_scan(self):
        """打开字体扫描工具"""
        self.font_scan_window = FontScanWindow()
        self.font_scan_window.show()

    def start_merge(self):
        """开始合并处理"""
        input_dir = self.input_edit.text()
        output_dir = self.output_edit.text()
        
        if not input_dir or not output_dir:
            self.log_text.append('请选择输入和输出目录！')
            return

        if not os.path.exists(input_dir):
            self.log_text.append(f'错误：输入目录 "{input_dir}" 不存在！')
            return

        # 重置停止标志
        if hasattr(process_mkv_files, 'should_stop'):
            delattr(process_mkv_files, 'should_stop')

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.worker = MergeWorker(
            input_dir=input_dir,
            output_dir=output_dir,
            execute=self.execute_checkbox.isChecked()
        )
        
        self.worker.log.connect(self.log_text.append)
        self.worker.finished.connect(self.on_merge_finished)
        self.worker.process_created.connect(self.on_process_created)
        self.worker.start()

    def stop_merge(self):
        """停止合并处理"""
        if self.worker:
            # 设置停止标志
            process_mkv_files.should_stop = True
            
            # 停止工作线程
            self.worker.stop()
            self.worker.wait()  # 等待线程结束
            self.worker = None
            
            # 终止进程
            if self.process and self.process.poll() is None:
                try:
                    if sys.platform == 'win32':
                        # 创建 startupinfo 对象
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                        subprocess.run(
                            ['taskkill', '/F', '/T', '/PID', str(self.process.pid)],
                            startupinfo=startupinfo,
                            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0,
                            check=True,
                            capture_output=True
                        )
                    else:
                        self.process.kill()
                    
                    # 等待进程完全终止
                    self.process.wait(timeout=5)
                    self.process = None
                    self.log_text.append('<font color="red">已停止合并操作</font>')
                    
                except Exception as e:
                    self.log_text.append(f'<font color="red">停止进程时出错: {str(e)}</font>')
                    import traceback
                    self.log_text.append(traceback.format_exc())
                
            # 恢复按钮状态
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def on_merge_finished(self):
        """合并完成或停止后的处理"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.process = None
        self.progress_bar.setVisible(False)  # 隐藏进度条
        if not self.execute_checkbox.isChecked():
            self.log_text.append('提示：命令已保存到当前目录下的 mergemkv.sh 文件中')

    def on_process_created(self, process):
        """保存新创建的进程"""
        self.process = process

    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if self.process and self.process.poll() is None:  # 检查进程是否还在运行
            reply = QMessageBox.question(
                self, 
                '确认退出',
                '任务正在进行中，确定要退出吗？',
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                defaultButton=QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    if sys.platform == 'win32':
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW | subprocess.STARTF_USESTDHANDLES
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                        subprocess.run(
                            ['taskkill', '/F', '/T', '/PID', str(self.process.pid)],
                            startupinfo=startupinfo,
                            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS if sys.platform == 'win32' else 0,
                            check=True,
                            capture_output=True
                        )
                    else:
                        self.process.kill()
                    
                    # 等待进程完全终止
                    self.process.wait(timeout=5)
                    self.process = None
                    self.log_text.append('<font color="red">已终止所有进程</font>')
                    
                except Exception as e:
                    self.log_text.append(f'<font color="red">停止进程时出错: {str(e)}</font>')
                    import traceback
                    self.log_text.append(traceback.format_exc())
                finally:
                    event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    @pyqtSlot(str)
    def append_log(self, text: str):
        """添加日志文本"""
        if text.startswith('<progress_start>'):
            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
        elif text.startswith('<progress_update>'):
            # 更新进度条
            try:
                progress = int(text.replace('<progress_update>', '').replace('</progress_update>', ''))
                self.progress_bar.setValue(progress)
            except (ValueError, IndexError):
                pass
        else:
            # 普通日志
            self.log_text.append(text)

def main():
    app = QApplication(sys.argv)
    window = MergeMkvWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 