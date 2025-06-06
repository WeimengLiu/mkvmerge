import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

class LogManager:
    _instance = None
    _initialized = False
    _log_dir = 'logs'  # 默认日志目录
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LogManager._initialized:
            self._setup_logger()
            LogManager._initialized = True
    
    def _setup_logger(self):
        """设置日志系统"""
        # 创建logger
        self.logger = logging.getLogger('MergeMKV')
        self.logger.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # 确保日志目录存在
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)
        
        # 创建按天rotating文件处理器
        log_file = os.path.join(self._log_dir, 'merge.log')
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=30,  # 保留30天的日志
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # 清除现有的处理器
        self.logger.handlers.clear()
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        
        # 设置不传递到父logger
        self.logger.propagate = False
    
    @classmethod
    def get_logger(cls):
        """获取logger实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance.logger
    
    @classmethod
    def get_log_dir(cls):
        """获取日志目录"""
        return cls._log_dir 