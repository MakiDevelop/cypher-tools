import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import os
from pathlib import Path
import threading
import logging
from datetime import datetime

# 添加本地 lib 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import pysubs2

# 設置日誌
def setup_logging():
    """設置日誌"""
    home = os.path.expanduser("~")
    log_dir = os.path.join(home, "Documents", "ASS轉SRT_logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"ass2srt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info(f"Python 路徑: {sys.path}")
    logging.info(f"當前工作目錄: {os.getcwd()}")
    logging.info(f"執行文件位置: {__file__}")

class SubtitleConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ASS 轉 SRT 工具")
        self.setup_ui()

    def setup_ui(self):
        # 文件選擇
        tk.Label(self.root, text="ASS 文件:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.file_path = tk.StringVar()
        tk.Entry(self.root, textvariable=self.file_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="選擇文件", command=self.select_file, width=10).grid(row=0, column=2, padx=5, pady=5)

        # 轉換按鈕
        convert_button = tk.Button(self.root, text="轉換為 SRT", command=self.start_convert, 
                                 bg="lightblue", width=20)
        convert_button.grid(row=1, column=1, pady=10)

        # 狀態標籤
        self.status_label = tk.Label(self.root, text="")
        self.status_label.grid(row=2, column=1, pady=5)

    def select_file(self):
        try:
            filepath = filedialog.askopenfilename(
                title="選擇 ASS 字幕文件",
                filetypes=[("ASS 字幕", "*.ass"), ("所有文件", "*.*")]
            )
            if filepath:
                self.file_path.set(filepath)
                logging.info(f"選擇文件: {filepath}")
        except Exception as e:
            logging.error(f"選擇文件時出錯: {str(e)}")
            messagebox.showerror("錯誤", f"選擇文件時出錯: {str(e)}")

    def start_convert(self):
        filepath = self.file_path.get()
        if not filepath:
            messagebox.showwarning("提示", "請選擇 ASS 文件")
            return
        
        # 在新線程中執行轉換
        threading.Thread(target=self.convert_to_srt, daemon=True).start()

    def convert_to_srt(self):
        input_path = self.file_path.get()
        try:
            self.status_label.config(text="正在轉換...")
            self.root.update()

            # 讀取 ASS 文件
            subs = pysubs2.load(input_path)

            # 生成輸出路徑
            output_path = str(Path(input_path).with_suffix('.srt'))
            
            # 轉換並保存
            subs.save(output_path, format_='srt')
            
            # 更新狀態
            self.status_label.config(text="轉換完成！")
            messagebox.showinfo("成功", f"已保存到：{output_path}")

        except Exception as e:
            self.status_label.config(text="轉換失敗！")
            messagebox.showerror("錯誤", f"轉換失敗: {str(e)}")

    def run(self):
        # 設置窗口大小和位置
        window_width = 700  # 增加窗口寬度
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 配置列寬度
        self.root.grid_columnconfigure(1, weight=1)  # 讓中間列可以擴展
        
        # 禁止調整窗口大小
        self.root.resizable(False, False)
        
        self.root.mainloop()

if __name__ == "__main__":
    try:
        setup_logging()
        logging.info("程式啟動")
        app = SubtitleConverter()
        app.run()
    except Exception as e:
        logging.exception("程式異常退出")
        raise