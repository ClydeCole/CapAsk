import logging
import yaml
from pathlib import Path
from ai import AiAsk

class MainError(Exception):
    pass

# ----------------------------------------------------------------------
# 全域設定
# ----------------------------------------------------------------------
CONFIG_FILE = Path(__file__).resolve().parent / "config.yaml"
DEFAULT_SCREENSHOT_DIR = Path(__file__).resolve().parent / "tmp"
log = logging.getLogger("main")

# ----------------------------------------------------------------------
# 工具函式
# ----------------------------------------------------------------------

#加載logging
def load_logging(debug: bool = False) -> None:
    """設定 root logger"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

# 加載配置文件
def load_config(path: Path) -> dict:
    """讀取 YAML 配置; 檔案不存在或格式錯誤時直接中止並提示."""
    if not path.is_file():
        raise SystemExit(f"[FATAL] 找不到配置檔: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise SystemExit(f"[FATAL] 配置檔格式錯誤: {e}") from e
    return data

# 加載保存路徑
def load_save_path(config_screencap: dict) -> Path:
    """
    :param config_screencap: 將config 內的screencap 輸入進來
    :return: 一個Path 路徑, 默認輸出為絕對路徑: /xxx/xxx/[項目根目錄]/tmp/screenshot.png
    """
    cap_dir = Path(config_screencap.get("save_dir", DEFAULT_SCREENSHOT_DIR)).resolve()
    cap_dir.mkdir(parents=True, exist_ok=True)
    cap_path = cap_dir / config_screencap.get("file_name", "screen.png")
    return cap_path

# 對手機畫面進行截圖
def screencap(device: int) -> None:
    if device == 1:
        # Termux 本地運行
        def capture():
            import screencap.root as screencap
            cap = screencap.Screencap()
            cap.capture()
        capture()

    elif device == 2:
        # adb 連接電腦
        def capture():
            import screencap.adb as screencap
            serial = cfg.get("serial", None)
            binary = cfg.get("binary", "adb")
            screencap.capture(serial, CAP_PATH, binary)
        capture()
    else:
        raise MainError(f"config.yaml 配置錯誤. [ device: {device} ]")

# 通過通知將答案發送給手機
def notify(device: int, message: str) -> None:
    from notify import adb
    from notify import root

    if device == 1:
        root.send_notify(cfg.get("notify_title", ""), message)
    elif device == 2:
        notify = adb.Notify(cfg)
        notify.send_notify(message)


# ----------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------

def wait() -> None:
    """
    等待使用者按下 音量鍵 + (KEY_VOLUMEUP) 後才繼續執行.

    檢測方式: 透過 subprocess 以 root 權限執行 `su -c getevent` 讀取
    /dev/input/event* 的原始按鍵事件. Android 的 SELinux 不允許一般
    Termux (untrusted_app) 讀取 /dev/input, 因此必須 root, 第一次執行
    時手機上會跳出 root 授權 (Magisk/SuperSU) 視窗.

    getevent 原始輸出的格式為: /dev/input/eventX: <type> <code> <value>
    音量鍵 + 的事件為:
        type  = 0001 (EV_KEY)
        code  = 0073 (0x73 = 115, KEY_VOLUMEUP)
        value = 00000001 (按下; 0=放開, 2=長按自動重複)
    """
    # ----------------------------------------------------------------------
    # AI 修改請注意!
    #
    # loop() 與 wait() 兩個函數部分全都為AI 生成,
    # 實測Termux 可以直接運行, 可能含有BUG
    # ----------------------------------------------------------------------

    import subprocess

    log.info("wait(): 請按下 音量鍵 + 以繼續 ...")
    proc = subprocess.Popen(
        ["su", "-c", "getevent"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        if proc.stdout is None:
            raise MainError("無法開啟 getevent 輸出")
        for line in proc.stdout:
            cols = line.split()
            # 範例: ['/dev/input/event3:', '0001', '0073', '00000001']
            if len(cols) >= 4:
                _, ev_type, code, value = cols[:4]
                if ev_type == "0001" and code == "0073" and value == "00000001":
                    log.info("偵測到 音量鍵 +, 繼續執行")
                    return
        # 能走到這裡代表 getevent 已結束 (通常是 root 授權被拒絕)
        raise MainError("getevent 提前結束: 請確認已授予 root 權限 (su -c getevent) 可正常運作")
    finally:
        # 結束流程時把 getevent 關掉, 避免留下孤兒程序
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()

def loop() -> None:
    while True:
        # 截圖
        screencap(cfg.get("device", 1))

        # ai 發送圖片
        ask = AiAsk(cfg)
        ai_result = ask.image()

        # 發短信
        notify(cfg.get("device", 1), ai_result)

        # 等待繼續信號 (音量鍵 +)
        wait()


# ----------------------------------------------------------------------
# 程式進入點
# ----------------------------------------------------------------------
if __name__ == '__main__':
    # 初始化 (只需要一次)
    cfg = load_config(CONFIG_FILE)
    load_logging(debug=bool(cfg.get("debug", False)))
    # 獲取文件保存路徑 (只需要一次)
    CAP_PATH = load_save_path(cfg.get("screencap", {'save_dir': 'tmp', 'file_name': 'screen.png'}))

    # 進入大循環
    loop()