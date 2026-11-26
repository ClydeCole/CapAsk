import ipaddress
import subprocess
import sys
import signal

def handle_sigint(signum, frame):
    print("\n已取消，程式結束。")
    sys.exit(130)
signal.signal(signal.SIGINT, handle_sigint)

def input_ip(prompt):
    """循環直到使用者輸入合法的IP 位址"""
    while True:
        value = input(prompt).strip()
        try :
            ipaddress.ip_address(value)
            return value
        except ValueError:
            print("IP 格式無效, 請重新輸入\n")

def input_port(prompt):
    """循環直到使用者輸入合法的連接埠號 (1-65535)"""
    while True:
        value = input(prompt).strip()
        if value.isdigit() and 1 <= int(value) <= 65535:
            return int(value)
        print("連接埠必須是1-65535 之間的數字, 請重新輸入\n")

def input_code(prompt):
    """循環直到使用者輸入合法的6 位數字驗證碼"""
    while True:
        value = input(prompt).strip()
        try:
            if len(value) == 6 and value.isdigit():
                return value
            else:
                raise ValueError("必须是 6 位数字")
        except ValueError as e:
            print(f"验证码无效（{e}），请重新输入\n")

def run_adb_pair(ip, port, code):
    """執行adb pair 並自動輸入驗證碼"""
    cmd = ["adb", "pair", f"{ip}:{port}"]
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(input=code + "\n", timeout=15)

        print(stdout)  # 正常應看到 "Successfully paired..."
        if stderr:
            print(stderr)
        return proc.returncode == 0

    except FileNotFoundError:
        print("找不到 adb 工具, 請確認已安裝並加入PATH")
        return False
    except subprocess.TimeoutExpired:
        print("adb pair 超時")
        return False

def run_adb_connect(ip, port):
    """執行adb connect"""
    cmd = ["adb", "connect", f"{ip}:{port}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0


if __name__ == '__main__':
    if input("如果第一次配對, 輸入任意內容回車, 否則直接回車\n: "):
        print("========================================")

        print("請打開無線偵錯")
        print("請在無線偵錯當中 點擊 [使用配對碼配對裝置]\n")
        print("示範: 255655")
        PAIR_CODE = input_code("請輸入 [Wi-Fi 配對碼] 下方的 6位數字\n: ")
        print("\n示範: 192.168.10.1")
        PAIR_IP = input_ip("請輸入 [IP 位址和通訊埠] 下方冒號 [:] 前方的數字(需要英文小數點)\n: ")
        print("\n示範: 25565")
        PAIR_PORT = input_port("請輸入 [IP 位址和通訊埠] 下方冒號 [:] 後方的數字\n: ")
        
        print(f"\n正在連接")
        run_adb_pair(ip=PAIR_IP, port=PAIR_PORT, code=PAIR_CODE)
        print("連接成功\n")

    print("========================================")
    print("\n示範: 192.168.10.1")
    CONNECT_IP = input_ip("請輸入 [IP 位址和通訊埠] 當中的IP\n: ")
    print("\n示範: 25565")
    CONNECT_PORT = input_port("請輸入 [IP 位址和通訊埠] 當中的埠\n: ")

    print(f"\n正在連接")
    run_adb_connect(ip=CONNECT_IP, port=CONNECT_PORT)
    print("連接成功\n")

    local_adb = input("是否設定本地連接埠adb 連接? (Y/n)\n: ")
    if local_adb == "Y" or local_adb == "y":
        subprocess.run(["adb", "tcpip", "55556"])
        subprocess.run(["adb", "disconnect", f"{CONNECT_IP}:{CONNECT_PORT}"])
        subprocess.run(["adb", "connect", "localhost:55556"])
        print("連接成功\n")

    print("全部設定完畢, 成功連接adb 偵錯")
    subprocess.run(["adb", "devices"])