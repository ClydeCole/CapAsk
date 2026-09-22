# CapAsk

透過ADB 截取Android 手機目前畫面, 交由AI 分析圖片中的題目並給出答案, 最後以Termux 通知把答案推回手機, 實現一鍵截圖答題的自動化流程.

## 功能

- 一鍵截圖: 自動偵測唯一連線的ADB 設備, 執行adb exec-out screencap 取得目前畫面並儲存為PNG 圖片.
- AI 答題: 將截圖上傳到OpenAI 相容API(預設使用DeepSeek), 由AI 分析圖片並回傳精簡答案.
- 手機通知: 透過adb shell 呼叫Termux 的termux-notification, 把AI 答案即時推送到手機.
- 全流程自動化: 一條指令即可完成 截圖 -> 上傳 -> 分析 -> 通知 的完整流程.
- 高度可配置: API 金鑰, 模型名稱, 提示詞, 截圖路徑, 通知標題等皆可在config.yaml 調整, 無需修改程式碼.
- 明確錯誤處理: 設備未連線, 截圖逾時, API 呼叫失敗等皆會拋出對應異常並提示原因.

## 使用方式

### 環境需求
- 軟體
  - Python 版本推薦**3.14** 其他版本應該也可以使用
  - 已安裝且可用的adb (Android Debug Bridge)
  - Python 套件: pyyaml (AI 呼叫使用內建標準庫, 無需安裝openai)
- Android
    - 一台已開啟USB 除錯並連線的Android 設備
    - 手機端已安裝Termux, 用於接收通知
    - 手機端已經獲取Root 權限, 用於`adb_notify.py` 發送通知信息
      - 未來會修改為無需Root 版本的
- Termux
  - 打開Termux 執行命令`pkg install termux-api`

### 安裝依賴

```
pip install pyyaml
```

### 設定config.yaml

至少需把ai.api_key 改為你自己的金鑰, 其餘可維持預設值.

### 執行

```
python main.py
```

各模組也可單獨執行  
那你可能需要在文件內簡單的配置一下
- `python adb_screencap.py`: 僅截取目前畫面.
- `python ai.py`: 僅上傳圖片並取得AI 答案.
- `python adb_notify.py`: 僅發送一則測試通知.

## 未來會開發的內容

1. 如果發生報錯, 將通過通知提醒, 使得無需離開手機畫面即可直接得知報錯情況
2. 將項目寫成一個大的循環, 通過點擊音量鍵 + 實現再次識別熒幕
3. Android Termux 直接運行項目, 無需通過USB 與PC 連接使用
4. 運行項目無需使用Root 權限即可直接使用
5. ~~待定~~

## 注意事項!!!!

> 你的`config.yaml` 文件內擁有你的API key, 如果需要分享`config.yaml` 請刪除API key

## 實現邏輯

整體執行流程如下:

config.yaml 讀取設定 -> 建立tmp 截圖目錄 -> adb 截取目前畫面(tmp/screen.png) -> 上傳圖片至AI -> AI 回覆答案 -> termux-notification 推送至手機

### main.py: 主程式

主程式負責串接三個模組:

1. load_config: 讀取config.yaml, 檔案不存在或格式錯誤時直接中止並提示.
2. setup_logging: 依debug 設定日誌等級(DEBUG 或INFO).
3. 建立截圖目錄(預設tmp), 並組出完整的截圖路徑.
4. 呼叫adb_screencap.capture 取得目前畫面.
5. 以AiAsk.image 將圖片送給AI 並取得答案.
6. 以Notify.send_notify 將答案推送到手機.

### adb_screencap.py: 截圖模組

- get_default_serial: 執行adb devices, 過濾state=device 的設備; 沒有設備或多台設備時拋出DeviceError, 提醒明確指定serial.
- capture: 組出adb -s <serial> exec-out screencap -p 指令, 直接把adb 輸出的PNG 位元組流寫入save_path; 10 秒逾時, 逾時或返回碼非0 皆視為失敗並拋出DeviceError.

### ai.py: AI 模組

1. AiAsk 初始化時讀取api_key 與base_url, 使用標準庫urllib 呼叫OpenAI 相容API, 只要是OpenAI 相容格式的API 皆可使用.
2. image: 讀取tmp/screen.png 的二進位內容, 以multipart/form-data 上傳到 /files (purpose=user_data) 取得file_id.
3. 以 POST /chat/completions 傳入system_prompt 與file_id, 依max_tokens 與timeout 取得AI 回覆, 最後回傳答案文字.

### adb_notify.py: 通知模組

- 組出adb shell su -c 指令, 在手機端以Termux 的termux-notification 發送通知.
- 通知標題取自notify.title, 內容為AI 回覆的答案; 返回碼非0 時拋出NotifyError.

### 錯誤處理

各模組統一拋出DeviceError, AiError, NotifyError, 讓上層(主程式) 可以集中兜底; 設備未連線, 截圖逾時, API 呼叫失敗等情況都會以明確訊息提示.