# -*- mode: python ; coding: utf-8 -*-
import os
import stat
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# 添加本地 lib 目錄
local_lib = os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'lib')
print(f"本地庫目錄: {local_lib}")

# 收集所有相關的依賴
all_hiddenimports = []
all_datas = []
all_binaries = []

# 在收集模塊部分添加調試輸出
print("開始收集依賴...")
for module in ['pysubs2']:
    print(f"正在收集 {module} 的依賴...")
    datas, binaries, hiddenimports = collect_all(module)
    print(f"找到的 datas: {datas}")
    print(f"找到的 binaries: {binaries}")
    print(f"找到的 hiddenimports: {hiddenimports}")
    all_datas.extend(datas)
    all_binaries.extend(binaries)
    all_hiddenimports.extend(hiddenimports)
    # 額外收集子模塊
    submodules = collect_submodules(module)
    print(f"找到的子模塊: {submodules}")
    all_hiddenimports.extend(submodules)

print(f"最終的 hiddenimports: {all_hiddenimports}")

# 在 runtime_hooks 中添加錯誤處理
runtime_hook_content = """
import sys
import traceback

def custom_excepthook(exc_type, exc_value, exc_traceback):
    with open('error.log', 'a', encoding='utf-8') as f:
        f.write(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = custom_excepthook
"""

with open('error_hook.py', 'w', encoding='utf-8') as f:
    f.write(runtime_hook_content)

a = Analysis(
    ['subtitle_converter.py'],
    pathex=[local_lib],  # 添加本地庫路徑
    binaries=[],
    datas=[
        ('lib/pysubs2', 'pysubs2'),  # 包含整個 pysubs2 目錄
    ],
    hiddenimports=['tkinter', 'chardet'] + all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['error_hook.py'],  # 添加錯誤處理鉤子
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
    name='ASS轉SRT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 改回 False
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
    name='ASS轉SRT',
)

app = BUNDLE(
    coll,
    name='ASS轉SRT.app',
    icon=None,
    bundle_identifier='com.yourname.ass2srt',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'LSEnvironment': {
            'PYTHONPATH': '@executable_path/../Resources/lib',
            'PYTHONHOME': '@executable_path/../Resources',
            'PATH': '@executable_path/../Resources:@executable_path/../Resources/lib:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
        },
        'CFBundleDocumentTypes': [{
            'CFBundleTypeName': 'ASS Subtitle',
            'CFBundleTypeExtensions': ['ass'],
            'CFBundleTypeRole': 'Viewer',
        }],
        'NSAppleEventsUsageDescription': 'Please allow access to execute scripts.',
        'NSRequiresAquaSystemAppearance': 'No',
        'NSDesktopFolderUsageDescription': '需要訪問文件以選擇和保存字幕文件',
        'NSDocumentsFolderUsageDescription': '需要訪問文件以選擇和保存字幕文件',
        'NSDownloadsFolderUsageDescription': '需要訪問文件以選擇和保存字幕文件',
    },
)

# 設置權限
def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2
    os.chmod(path, mode)

app_path = os.path.join('dist', 'ASS轉SRT.app')
if os.path.exists(app_path):
    for root, dirs, files in os.walk(app_path):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            os.chmod(dir_path, 0o755)
        for file in files:
            file_path = os.path.join(root, file)
            make_executable(file_path)