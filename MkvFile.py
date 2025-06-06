from os.path import expanduser, isfile
import json
from pymkv import MKVAttachment
from MKVTrack import MKVTrack
from Verification import verify_mkvmerge
from MKVInfo import MkvInfo, Track
from typing import Any, Optional, List, TypeVar, Type, cast, Callable
import subprocess as sp
import configparser
import os
import platform
from utils import get_mkvmerge_path
import sys

def str_add_quotes(x: Any) -> str:
    return str(x)

class MKVFile:
    mkvmerge_path: str
    file_path: str
    mkv_info: MkvInfo
    append_tracks: List[MKVTrack]
    append_attachments: List[MKVAttachment]
    config: configparser.ConfigParser

    def __init__(self, file_path) -> None:
        self.mkvmerge_path = get_mkvmerge_path()  # 使用通用函数获取路径
        self.file_path = file_path
        # 获取当前脚本文件的绝对路径
        script_path = os.path.abspath(__file__)
        script_directory = os.path.dirname(script_path)
        self.append_attachments = []
        self.append_tracks = []
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(script_directory,'command-map.ini'))

        # 只在第一次初始化时验证 mkvmerge
        if file_path is not None and not verify_mkvmerge(mkvmerge_path=self.mkvmerge_path):
            raise FileNotFoundError('未找到mkvmerge程序，请确保MKVToolNix已正确安装')
        if file_path is not None:
            # 创建启动信息对象
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = sp.STARTUPINFO()
                startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = sp.SW_HIDE

            # add file title
            file_path = expanduser(file_path)
            info_json = sp.check_output(
                [self.mkvmerge_path, '-J', file_path],
                startupinfo=startupinfo,
                creationflags=sp.CREATE_NO_WINDOW | sp.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            ).decode()
            self.mkv_info = MkvInfo.from_dict(json.loads(info_json))

    def add_track(self, track):
        if isinstance(track, str):
            self.append_tracks.append(MKVTrack(track))
        elif isinstance(track, MKVTrack):
            self.append_tracks.append(track)
        else:
            raise TypeError('track is not str or MKVTrack')

    def add_attachment(self, attachment):
        if isinstance(attachment, str):
            self.append_attachments.append(MKVAttachment(attachment))
        elif isinstance(attachment, MKVAttachment):
            self.append_attachments.append(attachment)
        else:
            raise TypeError('attachment is not str of MKVAttachment')
        

    def command(self, output_path, subprocess=False):
        output_path = expanduser(output_path)
        track_order = []
        mkv_info = self.mkv_info
        output_path = os.path.join(output_path, os.path.basename(mkv_info.file_name))
        file_name, file_ext = os.path.splitext(output_path)
        command = [self.mkvmerge_path, '-o', str_add_quotes(file_name + '.mkv')]
        if (mkv_info.container.properties.title):
            command.extend(['--title', mkv_info.container.properties.title])
        #不混流mkv文件中的字幕
        command.extend(["--no-subtitles"])
        #不混流attackments
        command.extend(["--no-attachments"])

        tracks = mkv_info.tracks
        file_id=0
        for track in tracks:
            track_id = str(track.id)
            trackProperties = track.properties
            if track.type == 'video' or track.type == 'audio':
                command.extend(['--compression', track_id + ':none'])
                command.extend(self.create_command(track_id, command_map_name='global-command', properties=trackProperties.to_dict()))
                if track.type == 'video':
                    command.extend(self.create_command(track_id, command_map_name='video-command', properties=trackProperties.to_dict()))
                track_order.append(str(file_id) + ':' + track_id)
        # add path
        command.append(str_add_quotes(self.file_path))
        
        for track in self.append_tracks:
            file_id=file_id+1
            command.extend(['--compression', str(track.track_id) + ':none'])
            if track.track_name is not None:
                command.extend(['--track-name', str_add_quotes(str(track.track_id) + ':' + track.track_name )])
            if track.language is not None:
                command.extend(['--language', str(track.track_id) + ':' + track.language])
            # add path
            command.append(str_add_quotes( track.file_path ))
            track_order.append(str(file_id) + ':' + str(track.track_id))

        # add attachments
        for attachment in self.append_attachments:
            # info
            if attachment.name is not None:
                command.extend(['--attachment-name', str_add_quotes(attachment.name)])
            if attachment.description is not None:
                command.extend(['--attachment-description', str_add_quotes(attachment.description)])
            if attachment.mime_type is not None:
                command.extend(['--attachment-mime-type', attachment.mime_type])

            # add path
            if not attachment.attach_once:
                command.extend(['--attach-file', str_add_quotes(attachment.file_path)])
            else:
                command.extend(['--attach-file-once', str_add_quotes(attachment.file_path)])

        command.extend(['--track-order',','.join(track_order)])
        
        if subprocess:
            # 添加更多参数来隐藏窗口
            command.extend([
                '--gui-mode'
            ])
            return command
        return " ".join(command)


    def create_command(self, track_id:str, command_map_name:str, properties:dict) -> List[str]:
        command = []
        if properties is None:
            return command
        config = self.config
        for key, value in properties.items():
            if value is None:
                continue
            command_prefix = config.get(command_map_name, key, fallback=None) 
            if command_prefix is not None:
                command_value = str_add_quotes( track_id + ':' + str(value)  )
                command.extend([command_prefix, command_value])
        
        return command

