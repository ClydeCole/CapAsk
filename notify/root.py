import logging
import subprocess

log = logging.getLogger(__name__)

class NotifyError(Exception):
    pass


def send_notify(title:str, message: str) -> None:
    cmd = ["termux-notification", "-t", title, "-c", message]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        raise NotifyError(proc.stderr.strip())
