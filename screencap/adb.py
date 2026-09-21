import logging
import subprocess
import time
from pathlib import Path

log = logging.getLogger(__name__)

class DeviceError(RuntimeError):
    pass

def get_default_serial(binary: str = "adb") -> str:
    """自動取得當前唯一連線的ADB 設備序列號."""
    try:
        res = subprocess.run([binary, "devices"], capture_output=True, text=True, check=True)
    except Exception as exc:
        raise DeviceError(f"無法執行{binary} devices: {exc}") from exc

    lines = res.stdout.strip().splitlines()[1:]  # 跳過第一行 "List of devices attached"
    devices = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
            log.info(f"設備獲取成功{devices}")

    if not devices:
        raise DeviceError("未檢測到已連線的ADB 設備(state=device)")
    if len(devices) > 1:
        raise DeviceError(f"檢測到多台設備{devices}, 請在serial 參數中明確指定一台")

    return devices[0]

def capture(serial: str = "", save_path: Path = "tmp/screen.png", binary: str = "adb") -> None:
    """
    擷取設備當前螢幕畫面並儲存為 PNG 圖片。
    :param serial: 設備序列號(adb devices 第一列); 若未填寫或為空則自動挑選唯一設備.
    :param save_path: 截圖檔案的儲存路徑, 預設為 "tmp/screen.png".
    :param binary: ADB 可執行檔名稱或路徑, 預設為 "adb".
    :return: None
    :raises DeviceError: 當 ADB 啟動失敗/執行超時或返回碼非0 時拋出。
    """

    if not serial:
        log.info("獲取設備序列號")
        serial = get_default_serial()

    # (1) 命令: adb -s <序列號> exec-out screencap -p
    cmd = [binary, "-s", serial, "exec-out", "screencap", "-p"]

    # (2) 執行：讓adb 的字節流寫入save_path 內
    try:
        with open(save_path, "wb") as fh:
            start = time.time()
            log.info("執行截圖")
            proc = subprocess.run(cmd, stdout=fh, timeout=10)
            log.info(f"截圖完畢, 消耗時間: {time.time() - start:.4f}s")

    except OSError as e:
        raise DeviceError(f"无法启动 adb: {e}") from e
    except subprocess.TimeoutExpired as e:
        raise DeviceError(f"screencap 超时(10s): {e}") from e

    # (3) 返回码非 0 = 失败（手机没连上、设备状态不对等）
    if proc.returncode != 0:
        raise DeviceError(
            f"screencap 失败 (exit={proc.returncode})，"
            f"先确认 adb devices 里 state=device"
        )

if __name__ == '__main__':
    capture()