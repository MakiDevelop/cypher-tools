# -*- mode: python ; coding: utf-8 -*-
import os
import stat

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
        'easyprocess',
        'tqdm'
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
            'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',
            'DYLD_LIBRARY_PATH': '@executable_path/../Resources'
        }
    },
)

# 設置權限
def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

# 等待 app bundle 創建完成後再設置權限
app_path = os.path.join('dist', '解壓工具.app')
if os.path.exists(app_path):
    # 設置整個 .app 目錄的權限
    for root, dirs, files in os.walk(app_path):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            os.chmod(dir_path, 0o755)
        for file in files:
            file_path = os.path.join(root, file)
            make_executable(file_path)
    
    # 特別設置 MacOS 目錄的權限
    macos_path = os.path.join(app_path, 'Contents', 'MacOS')
    if os.path.exists(macos_path):
        os.chmod(macos_path, 0o755)
        for file in os.listdir(macos_path):
            file_path = os.path.join(macos_path, file)
            if os.path.isfile(file_path):
                os.chmod(file_path, 0o755) 