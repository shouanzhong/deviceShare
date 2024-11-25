# pyinstaller -F -i icon.ico --key ailx10 main.py -n fserver
import os
import re
import subprocess
import time
import sys
from log import logging

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def get_devices():
    """
    获取设备序列号
    :return:
    """
    res = run_cmd("adb devices")
    devices = re.findall(r"^(\S+)\s+device", res, re.M)
    logging.debug("devices:")
    logging.debug(devices)
    return devices


def run_cmd(cmd: str):
    logging.debug(cmd)
    p = subprocess.run(cmd, shell=True, capture_output=True)
    output = p.stdout.decode(errors="ignore") + p.stderr.decode(errors="ignore")
    logging.debug(output)
    return output


def wait_device(device, timeout=10):
    run_cmd(f"adb -s {device} wait-for-device")
    for timeout in range(10):
        if device in get_devices():
            break
        time.sleep(1)

