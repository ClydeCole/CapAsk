import logging
import yaml
from pathlib import Path

from notify import Notify
# from notify.root import
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


# ----------------------------------------------------------------------
# 程式進入點
# ----------------------------------------------------------------------
if __name__ == '__main__':
    cfg = load_config(CONFIG_FILE)
    setup_logging(debug=bool(cfg.get("debug", False)))

    # 獲取文件保存路徑
    cap_cfg = cfg.get("screencap", {})
    cap_dir = Path(cap_cfg.get("save_dir", DEFAULT_SCREENSHOT_DIR))
    cap_dir.mkdir(parents=True, exist_ok=True)
    cap_path = cap_dir / cap_cfg.get("save_name", "screen.png")

    if cfg.get("device") == 1:
        # Termux 本地運行
        def capture():
            import screencap.root as screencap
            cap = screencap.Screencap()
            cap.capture()
        capture()

    elif cfg.get("device") == 2:
        # adb 連接電腦
        def capture():
            import screencap.adb as screencap
            serial = cfg.get("serial", None)
            binary = cfg.get("binary", "adb")
            screencap.capture(serial, cap_path, binary)
        capture()
    else:
        raise MainError(f"config.yaml 配置錯誤. [ device: {cfg.get('device')} ]")

    # ai 發送圖片
    ask = AiAsk(cfg)
    ai_result = ask.image()

    # 通過通知將答案發送給手機
    notify = Notify(cfg)
    notify.send_notify(ai_result)
