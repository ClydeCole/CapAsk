import subprocess
import logging
import time
from pathlib import Path

log = logging.getLogger(__name__)

class ScreenError(RuntimeError):
    pass

def screencap(save_path: Path, save_name: Path) -> None:
    cmd = ["su", "-c", "screencap", "-p", f"{save_path / save_name}"]
    start = time.time()
    log.info("執行截圖")
    try:
        subprocess.run(cmd, capture_output=True, timeout=10, text=True, check=True)
    except FileNotFoundError:
        raise ScreenError(f"找不到命令su. 你是否擁有或給予程序root 權限?")
    except subprocess.TimeoutExpired:
        raise ScreenError(f"截圖時間超時.")
    except subprocess.CalledProcessError as e:
        raise ScreenError(f"截圖失敗. 詳情: {e.stderr.strip()}")
    log.info(f"截圖完畢, 消耗時間: {time.time() - start:.4f}s")

if __name__ == '__main__':
    screencap(Path(__file__).parent / "tmp", Path(__file__).parent / "tmp" / "screenshot.png")
