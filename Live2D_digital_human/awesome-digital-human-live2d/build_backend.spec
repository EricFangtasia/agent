# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件 - 后端打包
使用方法: pyinstaller build_backend.spec
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集所有digitalHuman模块
hidden_imports = [
    'digitalHuman',
    'digitalHuman.agent',
    'digitalHuman.agent.core',
    'digitalHuman.bin',
    'digitalHuman.engine',
    'digitalHuman.engine.asr',
    'digitalHuman.engine.tts',
    'digitalHuman.protocol',
    'digitalHuman.utils',
    'fastapi',
    'uvicorn',
    'websockets',
    'edge_tts',
    'openai',
    'httpx',
    'pydub',
    'yacs',
]

# 添加所有digitalHuman子模块
hidden_imports += collect_submodules('digitalHuman')

# 需要打包的数据文件
datas = [
    ('configs', 'configs'),  # 配置文件目录
    ('assets', 'assets'),     # 资源文件目录
]

# 尝试收集edge_tts的数据文件
try:
    datas += collect_data_files('edge_tts')
except:
    pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DigitalHuman-Backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 显示控制台窗口，方便查看日志
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标路径
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DigitalHuman-Backend',
)
