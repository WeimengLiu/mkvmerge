# sheldon woodward
# 3/24/18

"""Verification functions for mkvmerge and associated files."""

import json
import os
from os.path import expanduser, isfile
from re import match
import subprocess as sp
import sys

# 添加在文件开头的全局变量
_mkvmerge_verified = {}

def verify_mkvmerge(mkvmerge_path='mkvmerge'):
    """Verify mkvmerge is working.

    mkvmerge_path (str):
        Alternate path to mkvmerge if it is not already in the $PATH variable.
    """
    # 检查缓存
    if mkvmerge_path in _mkvmerge_verified:
        return _mkvmerge_verified[mkvmerge_path]

    try:
        # 创建启动信息对象
        startupinfo = None
        if sys.platform == 'win32':
            startupinfo = sp.STARTUPINFO()
            startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = sp.SW_HIDE

        output = sp.check_output(
            [mkvmerge_path, '-V'],
            startupinfo=startupinfo,
            creationflags=sp.CREATE_NO_WINDOW | sp.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        ).decode()
        result = bool(match('mkvmerge.*', output))
        _mkvmerge_verified[mkvmerge_path] = result
        return result
    except (sp.CalledProcessError, FileNotFoundError):
        _mkvmerge_verified[mkvmerge_path] = False
        return False


def verify_matroska(file_path, mkvmerge_path='mkvmerge'):
    """Verify if a file is a Matroska file.

    file_path (str):
        Path of the file to be verified.
    mkvmerge_path (str):
        Alternate path to mkvmerge if it is not already in the $PATH variable.
    """
    if not verify_mkvmerge(mkvmerge_path=mkvmerge_path):
        raise FileNotFoundError('mkvmerge is not at the specified path, add it there or change the mkvmerge_path '
                                'property')
    if isinstance(file_path, os.PathLike):
        file_path = str(file_path)
    elif not isinstance(file_path, str):
        raise TypeError('"{}" is not of type str'.format(file_path))
    file_path = expanduser(file_path)
    if not isfile(file_path):
        raise FileNotFoundError('"{}" does not exist'.format(file_path))
    try:
        startupinfo = None
        if sys.platform == 'win32':
            startupinfo = sp.STARTUPINFO()
            startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = sp.SW_HIDE

        info_json = json.loads(sp.check_output(
            [mkvmerge_path, '-J', expanduser(file_path)],
            startupinfo=startupinfo,
            creationflags=sp.CREATE_NO_WINDOW | sp.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        ).decode())
    except sp.CalledProcessError:
        raise ValueError('"{}" could not be opened'.format(file_path))
    return info_json['container']['type'] == 'Matroska'


def verify_recognized(file_path, mkvmerge_path='mkvmerge'):
    """Verify a file is recognized by mkvmerge.

    file_path (str):
        Path to the file to be verified.
    mkvmerge_path (str):
        Alternate path to mkvmerge if it is not already in the $PATH variable.
    """
    if not verify_mkvmerge(mkvmerge_path=mkvmerge_path):
        raise FileNotFoundError('mkvmerge is not at the specified path, add it there or change the mkvmerge_path '
                                'property')
    if not isinstance(file_path, str):
        raise TypeError('"{}" is not of type str'.format(file_path))
    file_path = expanduser(file_path)
    if not isfile(file_path):
        raise FileNotFoundError('"{}" does not exist'.format(file_path))
    try:
        startupinfo = None
        if sys.platform == 'win32':
            startupinfo = sp.STARTUPINFO()
            startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = sp.SW_HIDE

        info_json = json.loads(sp.check_output(
            [mkvmerge_path, '-J', file_path],
            startupinfo=startupinfo,
            creationflags=sp.CREATE_NO_WINDOW | sp.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        ).decode())
    except sp.CalledProcessError:
        raise ValueError('"{}" could not be opened'.format(file_path))
    return info_json['container']['recognized']


def verify_supported(file_path, mkvmerge_path='mkvmerge'):
    """Verify a file is supported by mkvmerge.

    file_path (str):
        Path to the file to be verified.
    mkvmerge_path (str):
        Alternate path to mkvmerge if it is not already in the $PATH variable.
    """
    if not verify_mkvmerge(mkvmerge_path=mkvmerge_path):
        raise FileNotFoundError('mkvmerge is not at the specified path, add it there or change the mkvmerge_path '
                                'property')
    if not isinstance(file_path, str):
        raise TypeError('"{}" is not of type str'.format(file_path))
    file_path = expanduser(file_path)
    if not isfile(file_path):
        raise FileNotFoundError('"{}" does not exist'.format(file_path))
    try:
        # 创建启动信息对象
        startupinfo = None
        if sys.platform == 'win32':
            startupinfo = sp.STARTUPINFO()
            startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = sp.SW_HIDE
        info_json = json.loads(sp.check_output([mkvmerge_path, '-J', file_path],
                                               startupinfo=startupinfo,
                                               creationflags=sp.CREATE_NO_WINDOW | sp.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
                                               ).decode())
    except sp.CalledProcessError:
        raise ValueError('"{}" could not be opened')
    return info_json['container']['supported']
