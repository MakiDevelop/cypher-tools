# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['rar_extractor.py'],
    pathex=[],
    binaries=[('/usr/local/bin/unrar', '.')],  # 直接放在主目錄
    datas=[],
    hiddenimports=[
        'tkinter',
        'pyunpack',
        'patool',
        'py7zr',
        'easyprocess'
    ],
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
    name='解壓工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 改回 False 以隱藏終端窗口
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='解壓工具',
)

app = BUNDLE(
    coll,
    name='解壓工具.app',
    icon=None,
    bundle_identifier='com.yourname.extracttool',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'LSEnvironment': {
            'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
        }
    },
)

# 設置權限
import os
import stat
def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

if os.path.exists('dist'):
    for root, dirs, files in os.walk('dist'):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), 0o755)
        for file in files:
            make_executable(os.path.join(root, file)) 