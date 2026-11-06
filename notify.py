import logging
import subprocess

log = logging.getLogger(__name__)

class NotifyError(Exception):
    pass

def send_notify(title:str, message: str) -> None:
    """
    使用Termux 發送一則短信通知.
    :param title: 標題
    :param message : AI 回復信息
    :return: None
    """
    cmd = ["termux-notification", "-t", title, "-c", message]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        raise NotifyError("找不到termux-notification 命令. 您是否在Termux 中執行此程序? 否安裝了Termux-api?")
    except subprocess.CalledProcessError as e:
        raise NotifyError(f"通知發送失敗. 詳情: {e.stderr.strip()}") from e

if __name__ == '__main__':
    send_notify("a", "a")