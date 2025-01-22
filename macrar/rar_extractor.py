import py7zr
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import os
import shutil
import stat
from pathlib import Path
from pyunpack import Archive
from easyprocess import EasyProcess
import subprocess

def setup_unrar():
    """設置 UnRAR 工具"""
    if getattr(sys, 'frozen', False):
        # 如果是打包後的應用程序
        base_path = Path(sys._MEIPASS)
        unrar_path = base_path / 'unrar'
        if unrar_path.exists():
            # 確保有執行權限
            unrar_path.chmod(0o755)
            os.environ['PATH'] = f"{base_path}:{os.environ.get('PATH', '')}"
    else:
        # 開發環境使用系統的 unrar
        pass

    # 驗證 unrar 是否可用
    try:
        result = subprocess.run(['unrar', '-v'], 
                              capture_output=True, 
                              text=True, 
                              check=False)
        if result.returncode != 0:
            messagebox.showerror("錯誤", "UnRAR 工具初始化失敗")
            sys.exit(1)
    except Exception as e:
        messagebox.showerror("錯誤", f"UnRAR 工具檢查失敗: {str(e)}")
        sys.exit(1)

def extract_archive(archive_path, extract_path, password=None):
    """處理不同格式的壓縮文件"""
    file_ext = os.path.splitext(archive_path)[1].lower()
    
    try:
        if file_ext == '.7z':
            with py7zr.SevenZipFile(archive_path, mode='r', password=password) as z:
                z.extractall(path=extract_path)
        elif file_ext == '.rar':
            # 使用內置的 UnRAR 工具
            from pyunpack import Archive, PatoolError
            try:
                archive = Archive(archive_path)
                if password:
                    archive.extractall(extract_path, password=password)
                else:
                    archive.extractall(extract_path)
            except PatoolError as e:
                if "could not find an executable program" in str(e):
                    messagebox.showerror("錯誤", "UnRAR 工具初始化失敗")
                else:
                    raise e
        else:
            raise ValueError("不支援的文件格式")
    except Exception as e:
        raise e

# 初始化 GUI
def main():
    def select_archive_file():
        filepath = filedialog.askopenfilename(
            filetypes=[("壓縮文件", "*.rar *.7z")],
            title="選擇壓縮文件"
        )
        if filepath:
            archive_file_path.set(filepath)
            # 設置預設解壓目錄為壓縮文件所在目錄
            default_extract_path = os.path.dirname(filepath)
            extract_dir_path.set(default_extract_path)

    def select_extract_dir():
        dirpath = filedialog.askdirectory(title="選擇解壓目標文件夾")
        if dirpath:
            extract_dir_path.set(dirpath)

    def extract_file():
        archive_path = archive_file_path.get()
        extract_path = extract_dir_path.get()
        password = password_entry.get() or None

        if not archive_path:
            messagebox.showwarning("提示", "請選擇壓縮文件")
            return

        # 如果沒有指定解壓目錄，使用壓縮文件所在目錄
        if not extract_path:
            extract_path = os.path.dirname(archive_path)
            extract_dir_path.set(extract_path)

        try:
            # 創建進度條
            progress_window = tk.Toplevel(root)
            progress_window.title("解壓進度")
            progress_window.geometry("300x150")
            
            progress_label = tk.Label(progress_window, text="正在解壓中...")
            progress_label.pack(pady=10)
            
            progress_bar = ttk.Progressbar(progress_window, length=200, mode='indeterminate')
            progress_bar.pack(pady=10)
            progress_bar.start()

            # 解壓文件
            extract_archive(archive_path, extract_path, password)

            progress_window.destroy()
            messagebox.showinfo("成功", "文件解壓縮完成！")
        except Exception as e:
            progress_window.destroy() if 'progress_window' in locals() else None
            messagebox.showerror("錯誤", f"解壓失敗: {str(e)}")

    # Tkinter 窗口設置
    root = tk.Tk()
    root.title("壓縮文件解壓工具")

    # 文件選擇
    tk.Label(root, text="壓縮文件:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    archive_file_path = tk.StringVar()
    tk.Entry(root, textvariable=archive_file_path, width=50).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="選擇文件", command=select_archive_file).grid(row=0, column=2, padx=5, pady=5)

    # 目錄選擇
    tk.Label(root, text="解壓目標:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    extract_dir_path = tk.StringVar()
    tk.Entry(root, textvariable=extract_dir_path, width=50).grid(row=1, column=1, padx=5, pady=5)
    tk.Button(root, text="選擇目錄", command=select_extract_dir).grid(row=1, column=2, padx=5, pady=5)

    # 密碼輸入
    tk.Label(root, text="密碼 (可選):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    password_entry = tk.Entry(root, show="*", width=50)
    password_entry.grid(row=2, column=1, padx=5, pady=5)

    # 解壓按鈕
    tk.Button(root, text="解壓縮", command=extract_file, bg="lightblue").grid(row=3, column=1, pady=10)

    # 主循環
    root.mainloop()

if __name__ == "__main__":
    setup_unrar()
    main()