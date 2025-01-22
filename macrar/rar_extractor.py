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
import threading
from tqdm import tqdm

def setup_unrar():
    """設置 UnRAR 工具"""
    if getattr(sys, 'frozen', False):
        # 如果是打包後的應用程序
        if sys._MEIPASS:
            base_path = Path(sys._MEIPASS)
        else:
            # 如果是從應用程式資料夾運行
            base_path = Path(sys.executable).parent.parent / 'Resources'
        
        unrar_path = base_path / 'unrar'
        if unrar_path.exists():
            # 確保有執行權限
            unrar_path.chmod(0o755)
            os.environ['PATH'] = f"{base_path}:{os.environ.get('PATH', '')}"
            # 設置 DYLD_LIBRARY_PATH
            os.environ['DYLD_LIBRARY_PATH'] = f"{base_path}:{os.environ.get('DYLD_LIBRARY_PATH', '')}"
    else:
        # 開發環境使用系統的 unrar
        pass

    # 驗證 unrar 是否可用
    try:
        result = subprocess.run(['unrar', '-v'], 
                              capture_output=True, 
                              text=True, 
                              check=False,
                              env=os.environ)  # 使用更新後的環境變量
        if result.returncode != 0:
            messagebox.showerror("錯誤", "UnRAR 工具初始化失敗")
            sys.exit(1)
    except Exception as e:
        messagebox.showerror("錯誤", f"UnRAR 工具檢查失敗: {str(e)}")
        sys.exit(1)

def get_archive_size(archive_path):
    """獲取壓縮文件中所有文件的總大小"""
    total_size = 0
    file_ext = os.path.splitext(archive_path)[1].lower()
    
    try:
        if file_ext == '.7z':
            with py7zr.SevenZipFile(archive_path) as z:
                for info in z.list():
                    total_size += info.uncompressed
        elif file_ext == '.rar':
            # 使用 unrar 命令獲取文件列表
            result = subprocess.run(['unrar', 'l', archive_path], 
                                 capture_output=True, 
                                 text=True)
            # 解析輸出獲取文件大小
            for line in result.stdout.split('\n'):
                if line.strip() and 'Name' not in line and '-----------------' not in line:
                    try:
                        size = line.split()[1]
                        total_size += int(size)
                    except (IndexError, ValueError):
                        continue
    except Exception:
        return 0
    
    return total_size

def extract_with_progress(archive_path, extract_path, password, progress_var, progress_label):
    """帶進度的解壓函數"""
    file_ext = os.path.splitext(archive_path)[1].lower()
    total_size = get_archive_size(archive_path)
    
    try:
        if file_ext == '.7z':
            with py7zr.SevenZipFile(archive_path, mode='r', password=password) as z:
                extracted_size = 0
                for filename, bio in z.read().items():
                    target_path = os.path.join(extract_path, filename)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, 'wb') as f:
                        data = bio.read()
                        f.write(data)
                        extracted_size += len(data)
                        if total_size > 0:
                            progress = (extracted_size / total_size) * 100
                            progress_var.set(progress)
                            progress_label.config(text=f"已解壓: {progress:.1f}%")
        
        elif file_ext == '.rar':
            if password:
                cmd = ['unrar', 'x', '-p' + password, archive_path, extract_path]
            else:
                cmd = ['unrar', 'x', archive_path, extract_path]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            extracted_size = 0
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                if 'Extracting' in line:
                    extracted_size += 1
                    if total_size > 0:
                        progress = (extracted_size / total_size) * 100
                        progress_var.set(min(progress, 100))
                        progress_label.config(text=f"已解壓: {min(progress, 100):.1f}%")
            
            process.wait()
            if process.returncode != 0:
                raise Exception("解壓失敗")
    
    except Exception as e:
        raise e

def extract_archive(archive_path, extract_path, password=None):
    """處理不同格式的壓縮文件"""
    file_ext = os.path.splitext(archive_path)[1].lower()
    
    if file_ext not in ['.7z', '.rar']:
        raise ValueError("不支援的文件格式")
    
    return file_ext

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
            # 創建進度條窗口
            progress_window = tk.Toplevel(root)
            progress_window.title("解壓進度")
            progress_window.geometry("300x150")
            
            progress_label = tk.Label(progress_window, text="準備解壓...")
            progress_label.pack(pady=10)
            
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(progress_window, 
                                         length=200, 
                                         mode='determinate', 
                                         variable=progress_var)
            progress_bar.pack(pady=10)

            # 在新線程中執行解壓
            def extract_thread():
                try:
                    extract_with_progress(archive_path, extract_path, password, 
                                       progress_var, progress_label)
                    progress_window.destroy()
                    messagebox.showinfo("成功", "文件解壓縮完成！")
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("錯誤", f"解壓失敗: {str(e)}")

            threading.Thread(target=extract_thread, daemon=True).start()

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
    
    # 啟用密碼欄位的複製貼上功能
    def enable_paste(event=None):
        password_entry.event_generate('<<Paste>>')
        return "break"
    
    def enable_copy(event=None):
        password_entry.event_generate('<<Copy>>')
        return "break"
    
    def enable_cut(event=None):
        password_entry.event_generate('<<Cut>>')
        return "break"
    
    # 綁定快捷鍵
    password_entry.bind('<Command-v>', enable_paste)
    password_entry.bind('<Command-V>', enable_paste)
    password_entry.bind('<Command-c>', enable_copy)
    password_entry.bind('<Command-C>', enable_copy)
    password_entry.bind('<Command-x>', enable_cut)
    password_entry.bind('<Command-X>', enable_cut)
    
    # 添加右鍵選單
    def create_popup_menu(event):
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label="複製", command=enable_copy)
        menu.add_command(label="剪下", command=enable_cut)
        menu.add_command(label="貼上", command=enable_paste)
        menu.tk_popup(event.x_root, event.y_root)
    
    password_entry.bind('<Button-2>', create_popup_menu)  # macOS 右鍵
    password_entry.bind('<Button-3>', create_popup_menu)  # 其他系統右鍵

    # 解壓按鈕
    tk.Button(root, text="解壓縮", command=extract_file, bg="lightblue").grid(row=3, column=1, pady=10)

    # 主循環
    root.mainloop()

if __name__ == "__main__":
    setup_unrar()
    main()