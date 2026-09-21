import logging
import subprocess

import yaml

log = logging.getLogger(__name__)

class NotifyError(Exception):
    pass

class Notify:
    def __init__(self, cfg):
        notify_cfg = cfg.get("notify", {})
        self.title = notify_cfg.get("title")
        # 暫時寫入
        self.device = cfg.get("device")
        pass

    def send_notify(self, message):
        cmd = (
            "export PATH=/data/data/com.termux/files/usr/bin:$PATH; "
            f"/data/data/com.termux/files/usr/bin/termux-notification -t '{self.title}' -c '{message}'"
        )

        res = subprocess.run(["adb", "shell", f"su -c \"{cmd}\""], capture_output=True, text=True)

        if res.returncode != 0:
            raise NotifyError(res.stderr.strip())

if __name__ == "__main__":
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f.read())
    ntf = Notify(cfg)
    ntf.send_notify(message="[B]: 因为CPU主要功能是执行程序指令并进行运算，所以选择B。")