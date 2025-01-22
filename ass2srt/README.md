# cypher-tools
Cypher's side project

主要是建立自己常用的處理工具
特別是資料庫操作與Python的檔案與各類物件處理

有venv，請先 source bin/activate

## 字幕轉換工具（ass2srt）

### 使用方法

1. 下載字幕轉換工具
2. 字幕轉換工具.app
3. 選擇ass文件
4. 選擇輸出路徑
5. 轉換完成

### 打包
- 清理之前的構建
rm -rf lib
mkdir -p lib/pysubs2

- 安裝依賴
pip show pysubs2
cp -r $(pip show pysubs2 | grep Location | cut -d ' ' -f 2)/pysubs2/* lib/pysubs2/


- 重新打包
sudo rm -rf build dist
pyinstaller build_mac.spec
sudo chmod -R 755 "dist/ASS轉SRT.app"
sudo chown -R $USER "dist/ASS轉SRT.app"
codesign --force --deep --sign - "dist/ASS轉SRT.app"
