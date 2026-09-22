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
def setup_logging(debug: bool = False) -> None:
    """設定 root logger"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

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

# ----------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------

def load_save_path(config_screencap) -> Path:
    cap_dir = Path(config_screencap.get("save_dir", DEFAULT_SCREENSHOT_DIR)).resolve()
    cap_dir.mkdir(parents=True, exist_ok=True)
    cap_path = cap_dir / config_screencap.get("file_name", "screen.png")
    return cap_path

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

def notify(device: int, message: str) -> None:
    from notify import adb
    from notify import root
    # 通過通知將答案發送給手機
    if device == 1:
        root.send_notify(cfg.get("notify_title", ""), message)
    elif device == 2:
        notify = adb.Notify(cfg)
        notify.send_notify(message)

# ----------------------------------------------------------------------
# 程式進入點
# ----------------------------------------------------------------------
if __name__ == '__main__':
    # 初始化 (只需要一次)
    cfg = load_config(CONFIG_FILE)
    setup_logging(debug=bool(cfg.get("debug", False)))
    # 獲取文件保存路徑 (只需要一次)
    CAP_PATH = load_save_path(cfg.get("screencap", {'save_dir': 'tmp', 'file_name': 'screen.png'}))

    screencap(cfg.get("device", 1))

    # ai 發送圖片
    ask = AiAsk(cfg)
    ai_result = ask.image()

    notify(cfg.get("device", 1), ai_result)