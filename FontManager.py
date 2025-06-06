import os
import sqlite3
from typing import List, Dict, Set, Tuple, Optional, Union
import fontTools.ttLib as ttLib
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import signal
from contextlib import contextmanager
import time
import threading
import logging
from datetime import datetime
from LogManager import LogManager
from LogFormatter import LogFormatter
import sys
from utils import get_app_dir  # 从 utils 导入
import pysubs2  # 移到文件顶部

class FontManager:
    def __init__(self, max_workers: int = None):
        """
        初始化字体管理器
        :param max_workers: 最大线程数，默认为CPU核心数的2倍
        """
        # 直接使用相对路径
        self.db_path = 'fonts.db'
        self.max_workers = max_workers
        self.db_lock = Lock()  # 用于数据库操作的线程锁
        
        # 使用统一的日志系统
        self.logger = LogManager.get_logger()
        self.log = self.logger.info
        
        # 初始化数据库连接
        self.conn = None
        self._init_db()

    def __del__(self):
        """析构函数，确保数据库连接被正确关闭"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass

    def _setup_logger(self):
        """设置日志记录器"""
        # 创建logger
        logger = logging.getLogger(f'FontManager_{id(self)}')
        logger.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # 创建文件处理器（使用相对路径）
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_filename = os.path.join(log_dir, f'font_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # 创建控制台处理器
        #console_handler = logging.StreamHandler()
        #console_handler.setLevel(logging.INFO)
        #console_handler.setFormatter(formatter)
        
        # 清除现有的处理器
        logger.handlers.clear()
        
        # 添加处理器
        logger.addHandler(file_handler)
        #logger.addHandler(console_handler)  # 添加控制台输出
        
        # 设置不传递到父logger
        logger.propagate = False
        
        # 保存日志文件路径
        self.log_file = log_filename
        
        return logger

    def _log_separator(self):
        """输出分隔线"""
        self.log("-" * 80)

    def _get_connection(self):
        """获取数据库连接"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.conn

    def _init_db(self):
        """初始化数据库"""
        db_exists = os.path.exists(self.db_path)
        
        conn = self._get_connection()
        with self.db_lock:
            cursor = conn.cursor()
            if not db_exists:
                # 新建数据库
                self.log("创建新的字体数据库")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS fonts (
                        font_name TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        last_modified REAL NOT NULL,
                        file_size INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY (font_name, file_path)
                    )
                ''')
                conn.commit()
            else:
                # 验证现有数据库的结构
                self.log("使用现有字体数据库")
                cursor.execute("PRAGMA table_info(fonts)")
                columns = {row[1] for row in cursor.fetchall()}
                
                # 检查必要的字段是否都存在
                required_columns = {'font_name', 'file_path', 'last_modified', 'file_size'}
                if not required_columns.issubset(columns):
                    self.log("数据库结构不完整，需要重建...")
                    # 创建临时表
                    cursor.execute('''
                        CREATE TABLE fonts_temp (
                            font_name TEXT NOT NULL,
                            file_path TEXT NOT NULL,
                            last_modified REAL NOT NULL,
                            file_size INTEGER NOT NULL DEFAULT 0,
                            PRIMARY KEY (font_name, file_path)
                        )
                    ''')
                    
                    # 尝试迁移现有数据
                    try:
                        cursor.execute('''
                            INSERT OR REPLACE INTO fonts_temp 
                            (font_name, file_path, last_modified, file_size)
                            SELECT DISTINCT font_name, file_path, last_modified, file_size 
                            FROM fonts
                        ''')
                    except:
                        self.log("无法迁移旧数据")
                    
                    # 删除旧表并重命名新表
                    cursor.execute('DROP TABLE fonts')
                    cursor.execute('ALTER TABLE fonts_temp RENAME TO fonts')
                    
                    self.log("数据库结构更新完成")
                    conn.commit()
                else:
                    self.log("数据库结构正确，无需更新")

    class TimeoutException(Exception):
        pass

    @contextmanager
    def timeout(self, seconds: int):
        """Windows兼容的超时实现"""
        timer = None
        timeout_occurred = threading.Event()
        
        def on_timeout():
            timeout_occurred.set()
            
        try:
            timer = threading.Timer(seconds, on_timeout)
            timer.start()
            yield
        finally:
            if timer:
                timer.cancel()
                
        if timeout_occurred.is_set():
            raise self.TimeoutException("处理超时")

    def _process_font_file(self, font_path: Path) -> List[Tuple[str, str, float, int]]:
        """
        处理单个字体文件
        :return: List of (font_name, file_path, mtime, file_size)
        """
        results = []
        font_path_str = str(font_path)
        mtime = os.path.getmtime(font_path)
        file_size = os.path.getsize(font_path_str)
        font: Optional[ttLib.TTFont] = None
        names = set()  # 移到外层，收集所有字体名称

        try:
            self.log(f"处理字体文件: {font_path_str}")
            # 获取字体数量
            try:
                with open(font_path_str, 'rb') as f:
                    if f.read(4) == b'ttcf':  # 是TTC文件
                        f.seek(8)
                        num_fonts = int.from_bytes(f.read(4), byteorder='big')
                    else:
                        num_fonts = 1
            except Exception as e:
                self.log(f"读取字体数量失败: {font_path_str}")
                num_fonts = 1

            # 处理每个字体
            for font_index in range(num_fonts):
                try:
                    with self.timeout(5):
                        font = ttLib.TTFont(font_path, fontNumber=font_index, lazy=True)
                    
                    if 'name' not in font:
                        continue

                    for record in font['name'].names:
                        if record.nameID in (1, 4, 6):
                            try:
                                name = record.toUnicode()
                                if name and len(name.strip()) > 0:
                                    names.add(name.strip())
                            except (UnicodeDecodeError, Exception):
                                continue

                except self.TimeoutException:
                    self.log(f"处理超时: {font_path_str}")
                    break
                except Exception as e:
                    self.log(f"处理失败: {font_path_str} - {str(e)}")
                    continue
                finally:
                    if font:
                        try:
                            font.close()
                        except:
                            pass
                        font = None

            # 如果没有找到任何名称，使用文件名
            if not names:
                base_name = os.path.splitext(os.path.basename(font_path_str))[0]
                names.add(base_name)

            # 为每个名称创建记录
            for name in names:
                results.append((name, font_path_str, mtime, file_size))  # 移除 font_index

        except Exception as e:
            self.log(f"处理失败: {font_path_str} - {str(e)}")

        return results

    def _batch_update_db(self, font_data: List[Tuple[str, str, float, int]]):
        """
        批量更新数据库
        :param font_data: List of (font_name, file_path, mtime, file_size)
        """
        with self.db_lock:
            cursor = self._get_connection().cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO fonts 
                (font_name, file_path, last_modified, file_size)
                VALUES (?, ?, ?, ?)
            ''', font_data)
            self._get_connection().commit()

    def _log_section(self, title: str):
        """打印带标题的分隔区块"""
        self.log(LogFormatter.section(title))

    def _log_subsection(self, title: str):
        """打印带标题的子分隔区块"""
        self.log(LogFormatter.subsection(title))

    def scan_font_directory(self, font_dir: str, callback=None) -> None:
        try:
            self._log_section("字体库扫描")
            self.log(f"字体目录: {font_dir}")
            
            # 记录失败的文件
            failed_files = []
            
            # 获取所有字体文件（修改这部分）
            font_files = []
            for ext in ['.ttf', '.otf', '.ttc']:
                # 先获取根目录下的文件
                font_files.extend(list(Path(font_dir).glob(f'*{ext}')))
                # 再获取子目录下的文件
                font_files.extend(list(Path(font_dir).rglob(f'*/*{ext}')))
            
            # 去重
            font_files = list(set(font_files))
            
            total_files = len(font_files)
            if callback:
                callback(0, total_files)
                self.log(f"找到 {total_files} 个字体文件")

            # 获取需要处理的文件
            files_to_process = []
            existing_fonts = self._get_existing_fonts()
            for font_path in font_files:
                font_path_str = str(font_path)
                mtime = os.path.getmtime(font_path)
                if font_path_str not in existing_fonts or abs(existing_fonts[font_path_str] - mtime) >= 0.001:
                    files_to_process.append(font_path)

            if not files_to_process:
                if callback:
                    callback(total_files, total_files)
                    self.log("没有需要更新的字体文件")
                return

            processed_count = total_files - len(files_to_process)
            if callback:
                callback(processed_count, total_files)
                self.log(f"需要处理 {len(files_to_process)} 个文件")

            # 处理字体文件
            current_batch = []
            batch_size = 100
            success_count = 0
            error_count = 0

            for idx, font_file in enumerate(files_to_process):
                try:
                    results = self._process_font_file(font_file)
                    
                    if results:
                        current_batch.extend(results)
                        success_count += 1
                        
                        if len(current_batch) >= batch_size:
                            self._batch_update_db(current_batch)
                            current_batch = []
                    else:
                        error_count += 1
                        failed_files.append(str(font_file))

                    if callback:
                        current_progress = processed_count + idx + 1
                        callback(current_progress, total_files)
                        
                except Exception as e:
                    error_count += 1
                    failed_files.append(str(font_file))
                    self.log(f"处理失败: {font_file} - {str(e)}")

            # 处理剩余的批次
            if current_batch:
                self._batch_update_db(current_batch)

            # 清理不存在的记录
            self._cleanup_db(font_files)

            # 输出统计信息
            self._log_subsection("处理统计")
            self.log(f"总文件数: {len(files_to_process)}")
            self.log(f"成功: {success_count}")
            self.log(f"失败: {error_count}")
            
            # 输出失败文件列表
            if failed_files:
                self._log_subsection("处理失败的文件")
                for file in failed_files:
                    self.log(f"- {file}")

            if callback:
                callback(total_files, total_files)

        except Exception as e:
            self.log(f"扫描过程出错: {str(e)}")
            raise

    def _get_existing_fonts(self) -> Dict[str, float]:
        """获取数据库中现有的字体文件和修改时间"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT file_path, last_modified FROM fonts')
        return {row[0]: row[1] for row in cursor.fetchall()}

    def get_font_files_for_subtitle(self, subtitle_path: str, return_missing: bool = False) -> Union[List[str], Tuple[List[str], Set[str]]]:
        """
        从字幕文件中提取字体名称并返回对应的字体文件路径
        
        Args:
            subtitle_path: 字幕文件路径
            return_missing: 是否返回未找到的字体列表
            
        Returns:
            如果 return_missing 为 False，返回找到的字体文件路径列表
            如果 return_missing 为 True，返回 (找到的字体文件路径列表, 未找到的字体集合)
        """
        font_names = self._extract_fonts_from_subtitle(subtitle_path)
        font_files = set()
        missing_fonts = set()  # 收集未找到的字体

        if not font_names:
            return (list(font_files), missing_fonts) if return_missing else list(font_files)

        self._log_section("字体文件查找")
        with self.db_lock:
            cursor = self._get_connection().cursor()
            
            for font_name in font_names:
                self._log_subsection(f"查找字体: {font_name}")
                try:
                    # 只在GUI显示正在查找的字体名称
                    self.log(f"正在查找字体: {font_name}")
                    
                    # 以下SQL相关信息只记录到日志文件
                    query = '''
                        SELECT DISTINCT file_path, font_name
                        FROM fonts 
                        WHERE font_name = ? COLLATE NOCASE
                           OR font_name = ? COLLATE NOCASE
                           OR font_name = ? COLLATE NOCASE
                        ORDER BY file_size ASC
                        LIMIT 1
                    '''
                    
                    params = (
                        font_name,
                        f"{font_name} Regular",
                        f"{font_name} Normal"
                    )
                    
                    # 使用logger而不是log方法记录SQL信息
                    self.logger.debug(f"执行查询: {query}")
                    self.logger.debug(f"参数: {params}")
                    
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    
                    if result:
                        font_path, matched_name = result
                        self.logger.info(f"数据库匹配: {matched_name} -> {font_path}")
                        
                        if os.path.exists(font_path):
                            font_files.add(font_path)
                            self.log(f"✓ 找到字体: {font_path}")
                        else:
                            self.log(f'<font color="red">✗ 字体文件不存在: {font_path}</font>')
                            missing_fonts.add(font_name)  # 添加到未找到列表
                    else:
                        self.log(f'<font color="red">✗ 未找到字体: {font_name}</font>')
                        missing_fonts.add(font_name)  # 添加到未找到列表
                    
                except sqlite3.Error as e:
                    error_msg = f"数据库错误: {str(e)}"
                    self.logger.error(error_msg)
                    self.log(f'<font color="red">{error_msg}</font>')
                    continue
            
            # 在所有字体处理完成后，显示未找到的字体汇总
            if missing_fonts:
                self._log_subsection("未找到的字体汇总")
                self.log(f'<font color="red">总共有 {len(missing_fonts)} 个字体未找到:</font>')
                for font in sorted(missing_fonts):
                    self.log(f'<font color="red">- {font}</font>')
            
        return (list(font_files), missing_fonts) if return_missing else list(font_files)

    def _extract_fonts_from_subtitle(self, subtitle_path: str) -> Set[str]:
        """
        从字幕文件中提取字体名称
        
        Args:
            subtitle_path: 字幕文件路径
            
        Returns:
            字体名称集合
        """
        font_names = set()
        
        try:
            self._log_section("字幕字体分析")
            self.log(f"字幕文件: {subtitle_path}")
            
            # 使用 pysubs2 加载字幕文件
            subs = pysubs2.load(subtitle_path, encoding='utf-8-sig')
            
            # 1. 从样式中提取字体
            self._log_subsection("样式定义的字体")
            for style_name, style in subs.styles.items():
                if style.fontname:
                    self.log(f"Style [{style_name}] 使用字体: {style.fontname}")
                    font_names.add(style.fontname)
            
            # 2. 从对话行中提取内联字体
            self._log_subsection("行内定义的字体")
            inline_font_pattern = re.compile(r'\\fn([^\\}]+)')
            for line in subs:
                if not isinstance(line, pysubs2.SSAEvent):
                    continue
                
                matches = inline_font_pattern.findall(line.text)
                if matches:
                    self.log(f"在行 [{line.start/1000:.2f}s - {line.end/1000:.2f}s] 找到字体: {matches}")
                    font_names.update(matches)
            
            # 打印总结
            if font_names:
                self._log_subsection("提取结果")
                self.log(f"总共找到 {len(font_names)} 个字体:")
                for font in sorted(font_names):
                    self.log(f"- {font}")
            else:
                self.log("\n警告：未找到任何字体定义")
            
        except Exception as e:
            self.log(f"\n处理字幕文件时出错: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return set()
        
        return font_names

    def _cleanup_db(self, current_files: List[Path]):
        """
        清理数据库中不存在的记录
        :param current_files: 当前文件系统中的字体文件列表
        """
        with self.db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            # 获取数据库中的所有文件路径
            cursor.execute('SELECT DISTINCT file_path FROM fonts')
            db_files = set(row[0] for row in cursor.fetchall())
            
            # 当前文件系统中的文件路径
            current_paths = {str(f) for f in current_files}
            
            # 找出需要删除的文件路径
            files_to_delete = db_files - current_paths
            
            if files_to_delete:
                self._log_subsection("清理不存在的记录")
                for file_path in files_to_delete:
                    cursor.execute('DELETE FROM fonts WHERE file_path = ?', (file_path,))
                    self.log(f"- 删除: {file_path}")
                
                conn.commit() 