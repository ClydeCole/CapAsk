import subprocess
import logging
import time
from pathlib import Path
import yaml

log = logging.getLogger(__name__)

class DeviceError(RuntimeError):
    pass

class Screencap:
    def __init__(self):
        # 加載配置文件
        cfg = Path(__file__).parent.parent / "config.yaml"
        cfg = yaml.safe_load(cfg.read_text(encoding="utf-8"))

        # 儲存路徑
        self.__save_dir = Path(cfg.get("screencap", {}).get("save_dir", "tmp"))
        self.__save_dir.mkdir(parents=True, exist_ok=True)
        self.__save_name = cfg.get("screencap", {}).get("save_name", "screen.png")
        self.save_path = Path(__file__).parent.parent / self.__save_dir / self.__save_name


    def capture(self):
        cmd = ["su", "-c", "screencap", "-p", f"{self.save_path}"]
        start = time.time()
        log.info("執行截圖")
        proc = subprocess.run(cmd, capture_output=True, timeout=10)
        log.info(f"截圖完畢, 消耗時間: {time.time() - start:.4f}s")

        if proc.returncode != 0:
            raise DeviceError(
                f"screencap 失敗 (exit={proc.returncode})"
            )

if __name__ == '__main__':
    Screencap().capture()
