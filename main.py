import logging
import yaml
from pathlib import Path

from openai import OpenAI

import adb_screencap
import ai

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
    cap_path = cap_dir / cap_cfg.get("filename", "screen.png")

    # adb 連接電腦
    serial = cfg.get("serial", None)
    binary = cfg.get("binary", "adb")
    adb_screencap.capture(serial, cap_path, binary)

    # ai 發送圖片
    ask = ai.AiAsk(cfg)
    ask.image()