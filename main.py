import logging
import yaml
from pathlib import Path

class MainError(Exception):
    pass

# ----------------------------------------------------------------------
# 全域設定
# ----------------------------------------------------------------------
CONFIG_FILE = Path(__file__).resolve().parent / "config.yaml"
log = logging.getLogger("main")

# ----------------------------------------------------------------------
# 工具函式
# ----------------------------------------------------------------------

#加載logging
def load_logging(debug: bool = False) -> None:
    """設定root logger"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

# 加載配置文件
def load_config_file(config_path: Path) -> dict:
    """
    讀取 YAML 配置
    :param config_path: Yaml 配置文件的Path 地址
    :return: 一個配置文件的字典
    """
    if not config_path.is_file():
        raise SystemExit(f"[FATAL] 找不到配置檔: {config_path}")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise SystemExit(f"配置檔格式錯誤: {e}") from e
    return config_data


class CapAsk:
    def __init__(self):
        self.cfg = None
        self.file_full_path = None
        self.load_base()

    def reload_config(self):
        """
        重新讀取並加載配置文件.
        """
        self.load_base()

    def load_base(self) -> None:
        """
        加載基礎配置選項, 包含:
        - 重新加載Yaml 配置數據
        - 重新加載文件保存路徑
        """
        self.cfg = load_config_file(CONFIG_FILE)                                        # CONFIG 檔案
        cfg_screencap = (self.cfg.get("screencap", {'save_dir': 'tmp', 'file_name': 'screen.png'}))
        dir_path = Path(cfg_screencap.get("save_dir", "tmp")).resolve()                 # 截圖檔案路徑
        dir_path.mkdir(parents=True, exist_ok=True)
        self.file_full_path = dir_path / cfg_screencap.get("file_name", "screen.png")   # 截圖檔案路徑 + 名稱

    def screencap(self) -> None:
        """對手機畫面進行截圖"""
        from screencap.root import screencap
        screencap(self.file_full_path)

    def send_notify(self, message: str) -> None:
        """通過通知將答案發送給手機"""
        from notify import notify
        notify(self.cfg.get("notify_title", ""), message)


# ----------------------------------------------------------------------
# 程式進入點
# ----------------------------------------------------------------------
if __name__ == '__main__':
    capask = CapAsk()
    load_logging(debug=bool(capask.cfg.get("debug", False)))

    if capask.cfg.get("root") == 0:
        print("UniAutomator")
    elif capask.cfg.get("root") == 1:
        capask.send_notify("aaa")
    else:
        raise MainError(f"{capask.file_full_path}")


    # # 進入大循環
    # loop(cfg.get("volume_wait_time", 5))