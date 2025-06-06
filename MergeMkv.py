#!/usr/bin/python3
from MKVTrack import MKVTrack
from MkvFile import MKVFile
from FontManager import FontManager
from LogManager import LogManager
from LogFormatter import LogFormatter
import subprocess as sp
import os
import sys
from rich.console import Console
import logging as logger
import coloredlogs

def process_mkv_files(directory: str, output: str, execute: bool = False, print_command: bool = False) -> None:
    """
    处理MKV文件的主要逻辑
    
    Args:
        directory: 输入目录路径
        output: 输出目录路径
        execute: 是否执行合并命令
        print_command: 是否打印命令
    """
    logger = LogManager.get_logger()
    font_manager = FontManager()
    all_missing_fonts = set()  # 收集所有文件的未找到字体
    
    logger.info(LogFormatter.section("MKV文件处理"))
    logger.info(f"输入目录: {directory}")
    logger.info(f"输出目录: {output}")
    
    # 确保输出目录存在
    os.makedirs(output, exist_ok=True)
    
    # 清空 mergemkv.sh 文件
    if print_command or not execute:
        with open("./mergemkv.sh", "w", encoding='utf-8') as f:
            f.write("")  # 清空文件内容
    
    # 递归遍历输入目录
    for root, dirs, files in os.walk(directory):
        # 计算当前目录对应的输出目录
        relative_path = os.path.relpath(root, directory)
        current_output = os.path.join(output, relative_path)
        os.makedirs(current_output, exist_ok=True)
        
        # 处理视频文件
        for file in files:
            if not file.lower().endswith(('.mkv', '.m2ts')):
                continue
                
            logger.info(LogFormatter.subsection(f"处理文件: {file}"))
            
            # 检查是否被要求停止
            if hasattr(process_mkv_files, 'should_stop') and process_mkv_files.should_stop:
                logger.info('<font color="red">收到停止信号，终止处理</font>')
                return
                
            input_file = os.path.join(root, file)
                    
            mkv_file = MKVFile(input_file)
            file_name, _ = os.path.splitext(file)
            
            # 记录需要复制的字幕文件
            subtitle_files = []
            
            # 检查字幕文件
            logger.info(LogFormatter.subsection("字幕检查"))
            for ass_suffix in ['.ass', '.zh.ass']:
                ass_file_name = file_name + ass_suffix
                ass_file_path = os.path.join(root, ass_file_name)
                if not os.path.exists(ass_file_path):
                    continue
                    
                logger.info(LogFormatter.list_item(f'Find ASS file: {ass_file_name}'))
                subtitle_files.append((ass_file_path, ass_file_name))  # 记录字幕文件
                
                # 获取字幕使用的字体和未找到的字体
                font_files, missing = font_manager.get_font_files_for_subtitle(ass_file_path, return_missing=True)
                all_missing_fonts.update(missing)

                if font_files:
                    logger.info(LogFormatter.list_item(f'Found {len(font_files)} fonts for subtitle'))
                    for font_file in font_files:
                        if os.path.exists(font_file):
                            font_name = os.path.basename(font_file)
                            logger.info(LogFormatter.list_item(f'Adding font: {font_name}'))
                            mkv_file.add_attachment(font_file)
                        else:
                            logger.warning(LogFormatter.list_item(f'Font file not found: {font_file}'))
                
                # 添加字幕轨道
                ass_file_track = MKVTrack(
                    ass_file_path,
                    track_name="简体中文",
                    default_track=True,
                    language="chi"
                )
                mkv_file.add_track(ass_file_track)

            # 生成命令
            logger.info(LogFormatter.subsection("执行合并"))
            command = mkv_file.command(current_output)

            if print_command or not execute:
                logger.info(LogFormatter.section('Merge Command:'))
                logger.info(command)
                with open("./mergemkv.sh", "a", encoding='utf-8') as f:
                    f.write(command + "\n")

            if not execute:
                logger.info('仅生成命令，不执行合并')
                continue

            logger.info('Running with command:')
            logger.info(command)
            try:
                # 创建启动信息对象
                startupinfo = None
                if sys.platform == 'win32':
                    startupinfo = sp.STARTUPINFO()
                    startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = sp.SW_HIDE

                process = sp.Popen(
                    mkv_file.command(output, subprocess=True),
                    stdout=sp.PIPE,
                    stderr=sp.STDOUT,
                    stdin=sp.DEVNULL,
                    encoding='utf-8',
                    bufsize=1,
                    errors='replace',
                    startupinfo=startupinfo,
                    creationflags=(
                        sp.CREATE_NO_WINDOW |
                        sp.DETACHED_PROCESS |
                        sp.CREATE_NEW_PROCESS_GROUP
                    ) if sys.platform == 'win32' else 0
                )
                
                # 发送进程创建信号
                if hasattr(process_mkv_files, 'process_created_callback'):
                    process_mkv_files.process_created_callback(process)
                
                progress_shown = False  # 标记是否已显示进度
                
                while True:
                    # 检查是否被要求停止
                    if hasattr(process_mkv_files, 'should_stop') and process_mkv_files.should_stop:
                        process.terminate()
                        logger.info('<font color="red">收到停止信号，终止处理</font>')
                        return
                        
                    output_line = process.stdout.readline()
                    if output_line == '' and process.poll() is not None:
                        break
                    if output_line:
                        line = output_line.strip()
                        
                        # 处理进度信息
                        if line.startswith('#GUI#progress'):
                            try:
                                current_progress = int(line.split()[-1].rstrip('%'))
                                # 第一次显示进度
                                if not progress_shown:
                                    logger.info(f'<progress_start>合并进度: {current_progress}%</progress_start>')
                                    progress_shown = True
                                else:
                                    # 更新进度
                                    logger.info(f'<progress_update>{current_progress}</progress_update>')
                            except (ValueError, IndexError):
                                pass
                        # 处理其他信息
                        elif 'warning' in line.lower():
                            logger.warning(LogFormatter.warning(line))
                        elif 'error' in line.lower():
                            logger.error(LogFormatter.error(f'Failed to process {file}: {line}'))
                        elif not line.startswith('#GUI#') and not line.startswith('｢'):  # 忽略GUI和文件信息
                            logger.info(line)
                
                return_code = process.poll()
                if return_code == 0:
                    logger.info(LogFormatter.success('Successfully processed: ' + output))
                    
                    # 在命令执行成功后复制字幕文件
                    logger.info(LogFormatter.subsection("复制字幕文件"))
                    for src_path, ass_file_name in subtitle_files:
                        output_ass_path = os.path.join(output, ass_file_name)
                        try:
                            import shutil
                            shutil.copy2(src_path, output_ass_path)
                            logger.info(LogFormatter.success(f'字幕文件已复制到: {output_ass_path}'))
                        except Exception as e:
                            logger.error(LogFormatter.error(f'复制字幕文件失败: {str(e)}'))
                else:
                    logger.error(LogFormatter.error(f'Failed to process {file} with return code {return_code}'))
                
            except sp.CalledProcessError as e:
                logger.error(LogFormatter.error(f'Failed to process {file}: {str(e)}'))

    # 在所有文件处理完成后，显示所有未找到的字体汇总
    if all_missing_fonts:
        logger.info(LogFormatter.section("所有未找到的字体汇总"))
        logger.info(f'<font color="red">总共有 {len(all_missing_fonts)} 个字体未找到:</font>')
        for font in sorted(all_missing_fonts):
            logger.info(f'<font color="red">- {font}</font>')
    
    logger.info(LogFormatter.section('All files processed'))


