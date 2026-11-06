import re
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET


class XMLError(RuntimeError):
    pass

BOUNDS = re.compile(r'\[(-?\d+),(-?\d+)]\[(-?\d+),(-?\d+)]')

def get_xml_path(device: int) -> tuple:
    """
    :return: remote_xml_file_path, local_xml_file_path
    """
    local_path = Path(__file__).parent.parent / "tmp" / "window_dump.xml"

    if device == 1:
        return None, local_path
    elif device == 2:
        return Path("/sdcard/window_dump.xml"), local_path

    raise XMLError(f"你的yaml 配置檔案 device:{device} 選項配置錯誤, 請檢查配置文件")

def get_screen_texts(device: int, binary: str = "adb", serial: str = "") -> list[str]:
    """回傳目前螢幕上的所有文字 (由上到下, 由左到右, 已去重).
    :param device: yaml 配置項的device: 選擇. 1/2
    :param serial: adb 設備序列號. 同時接多台手機時才需要指定, 留空代表讓adb 自己選擇
    :param binary: adb 執行檔名稱或完整路徑.
    :return: 文字清單, 例如 ["設定", "Wi-Fi", "藍牙"].
    """
    xml_r, xml_l = get_xml_path(device)

    # 1. 創建adb 命令
    cmd = [binary]
    if serial:
        cmd = [binary, "-s", serial]

    # 2. 叫手機產生XML 檔案
    xml = subprocess.run(
        # device: 1, xml_l: ./tmp/window_dump.xml
        # device: 2, xml_r: /sdcard/window_dump.xml
        cmd + ["shell", "uiautomator", "dump", str(xml_l) if not xml_r else str(xml_r)],
        capture_output=True, text=True, check=True
    )

    # 將產生的XML 檔案, 丟給解析
    if device == 1:
        return _parse_xml(xml.stdout)

    # 3. 如果程序是在電腦上執行, 則將手機上的XML 檔案複製到電腦
    xml = subprocess.run(
        cmd + ["exec-out", "cat", str(xml_r)],
        capture_output=True, text=True, check=True
    ).stdout
    return _parse_xml(xml)

def _parse_xml(xml: str) -> list[str]:
    """把 UI 階層 XML 轉成文字清單."""
    items = []
    # 每個 <node> 就是一個控制項, 循環獲得node
    for node in ET.fromstring(xml).iter("node"):
        # 拿到文本, 如果還是得不到任何文本就continue 了
        text = (node.get("text") or "").strip() or (node.get("content-desc") or "").strip()
        if not text:
            continue

        match = BOUNDS.match(node.get("bounds") or "")
        # group(1)=左邊框x, group(2)=上邊框y, group(3)=右x, group(4)=下y.
        y, x = (int(match.group(2)), int(match.group(1))) if match else (0, 0)
        # 先用 (y, x) 當排序鍵存起來:
        #   y = 上緣座標, 越小越上面
        #   x = 左緣座標, 越小越左邊
        items.append(((y, x), text))
    items.sort()

    return list(dict.fromkeys(text for _, text in items))

if __name__ == '__main__':
    all_texts = get_screen_texts(device=2, binary="adb")
    print("\n".join(all_texts))