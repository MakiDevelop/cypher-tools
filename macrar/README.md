# cypher-tools
Cypher's side project

主要是建立自己常用的處理工具
特別是資料庫操作與Python的檔案與各類物件處理

有venv，請先 source bin/activate

## 解壓工具（macrar）

### 使用方法

1. 下載解壓工具
2. 解壓工具.app
3. 選擇壓縮文件
4. 選擇解壓路徑
5. 解壓完成

### 打包
- 清理之前的構建
sudo rm -rf build dist

- 安裝依賴
pip install -r requirements.txt

- 重新打包
pyinstaller build_mac.spec

- 設置權限
sudo chmod -R 755 dist/解壓工具.app
sudo chown -R $USER dist/解壓工具.app

- 代碼簽名
codesign --force --deep --sign - "dist/解壓工具.app"
