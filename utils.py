import os
import platform
import winreg
import subprocess
import logging
import sys

logger = logging.getLogger(__name__)

# 添加缓存
_mkvmerge_path_cache = None

def get_app_dir():
    """获取应用程序运行目录"""
    if getattr(sys, '_MEIPASS', False):
        # 如果是打包后的exe，使用当前工作目录
        return os.getcwd()
    else:
        # 如果是python脚本
        return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def get_mkvmerge_path() -> str:
    """
    获取mkvmerge可执行文件的路径，使用缓存避免重复查找
    
    Returns:
        str: mkvmerge可执行文件的完整路径，如果未找到则返回'mkvmerge'
        
    Note:
        Windows: 从注册表和常见安装路径查找MKVToolNix
        其他系统: 默认使用'mkvmerge'命令
    """
    global _mkvmerge_path_cache
    
    if _mkvmerge_path_cache is not None:
        return _mkvmerge_path_cache
        
    logger.info("开始查找 mkvmerge 路径...")
    
    if platform.system() == 'Windows':
        try:
            # 尝试从注册表获取MKVToolNix安装路径
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MKVToolNix',
                              0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                install_path = winreg.QueryValueEx(key, 'InstallLocation')[0]
                mkvmerge_path = os.path.join(install_path, 'mkvmerge.exe')
                if os.path.exists(mkvmerge_path):
                    logger.info(f"从64位注册表找到 mkvmerge: {mkvmerge_path}")
                    _mkvmerge_path_cache = mkvmerge_path
                    return mkvmerge_path
                
        except WindowsError:
            logger.debug("64位注册表查找失败，尝试32位注册表")
            try:
                # 尝试从32位注册表获取
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MKVToolNix',
                                  0, winreg.KEY_READ) as key:
                    install_path = winreg.QueryValueEx(key, 'InstallLocation')[0]
                    mkvmerge_path = os.path.join(install_path, 'mkvmerge.exe')
                    if os.path.exists(mkvmerge_path):
                        logger.info(f"从32位注册表找到 mkvmerge: {mkvmerge_path}")
                        _mkvmerge_path_cache = mkvmerge_path
                        return mkvmerge_path
            except WindowsError:
                logger.debug("注册表查找失败")
            
        # 如果注册表查找失败，尝试常见安装路径
        common_paths = [
            r'C:\Program Files\MKVToolNix',
            r'C:\Program Files (x86)\MKVToolNix',
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'MKVToolNix'),
            os.path.join(os.environ.get('APPDATA', ''), 'MKVToolNix'),
        ]
        
        logger.debug("检查常见安装路径...")
        for path in common_paths:
            mkvmerge_path = os.path.join(path, 'mkvmerge.exe')
            if os.path.exists(mkvmerge_path):
                logger.info(f"在常见路径找到 mkvmerge: {mkvmerge_path}")
                _mkvmerge_path_cache = mkvmerge_path
                return mkvmerge_path
    
    # 在PATH中查找mkvmerge
    logger.debug("在系统PATH中查找mkvmerge...")
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['where', 'mkvmerge'], capture_output=True, text=True)
        else:
            result = subprocess.run(['which', 'mkvmerge'], capture_output=True, text=True)
        if result.returncode == 0:
            mkvmerge_path = result.stdout.strip().split('\n')[0]
            logger.info(f"在PATH中找到 mkvmerge: {mkvmerge_path}")
            _mkvmerge_path_cache = mkvmerge_path
            return mkvmerge_path
    except Exception as e:
        logger.debug(f"PATH查找失败: {str(e)}")
    
    logger.warning("未找到 mkvmerge，将使用默认值 'mkvmerge'")
    _mkvmerge_path_cache = 'mkvmerge'
    return _mkvmerge_path_cache

def verify_mkvmerge(mkvmerge_path: str) -> bool:
    """
    验证mkvmerge是否可用
    
    Args:
        mkvmerge_path: mkvmerge可执行文件路径
        
    Returns:
        bool: 如果mkvmerge可用返回True，否则返回False
    """
    try:
        result = subprocess.run([mkvmerge_path, '--version'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0 and 'mkvmerge' in result.stdout.lower():
            logger.info(f"验证mkvmerge成功: {mkvmerge_path}")
            logger.debug(f"mkvmerge版本信息: {result.stdout.strip()}")
            return True
    except Exception as e:
        logger.error(f"验证mkvmerge失败: {str(e)}")
    return False 