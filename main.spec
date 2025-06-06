# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# 获取当前平台
platform = sys.platform

# 根据平台设置图标
icon_file = 'icon.ico' if platform == 'win32' else 'icon.icns' if platform == 'darwin' else None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('command-map.ini', '.'),
        ('icon.ico', '.'),
    ],
    hiddenimports=[
        'pysubs2',
        'fontTools',
        'fontTools.ttLib',
        'pymkv',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'test',
        'unittest',
        'email',
        'html',
        'http',
        'xml',
        'pydoc',
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure, optimize=2)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MkvMergeGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=platform == 'darwin',  # 在 macOS 上启用 argv 模拟
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file
)

# 在 macOS 上创建 .app 包
if platform == 'darwin':
    app = BUNDLE(
        exe,
        name='MkvMergeGUI.app',
        icon=icon_file,
        bundle_identifier='com.mkvmerge.gui',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'NSRequiresAquaSystemAppearance': 'False',  # 支持暗黑模式
        },
    )
