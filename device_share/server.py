import os
import re
import subprocess
import sys
import time

import win32api
import win32con
from flask import Flask, request, render_template_string, redirect, url_for
from gevent import pywsgi

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from forward import ForwardTool
from log import logging
from device_share import get_devices, wait_device, run_cmd, config

app = Flask(__name__)
f = ForwardTool()

# 设备与转发端口
port_dict = {}
model_dict = {}
host_addr = None


def get_model(device: str):
    global model_dict
    m = model_dict.get(device, None)
    if not m:
        m = run_cmd(f"adb -s {device} shell getprop ro.product.model").strip()
    model_dict[device] = m
    return m


def device_forward(device: str, retry=False):
    global port_dict
    run_cmd(f"adb -s {device} wait-for-device")
    forward_list = run_cmd(f"adb -s {device} forward --list")
    ports = None
    if forward_list.strip():
        ports = re.findall(r"%s tcp:(\d+)" % device, forward_list)
    if ports:
        port = ports[0]
    else:
        run_cmd(f"adb -s {device} tcpip 5555")
        wait_device(device)
        run_cmd("adb devices")
        port = run_cmd(f"adb -s {device} forward --no-rebind tcp:0 tcp:5555")
        if not re.search(r'\d+', port):
            if retry:
                time.sleep(1)
                device_forward(device=device, retry=False)
            else:
                return  # 不再尝试
    logging.info("port forward to localhost=======[%s]" % port)
    f.ports_forward(int(port))
    # run_cmd(f"netsh interface portproxy add v4tov4 listenport={port} connectaddress=localhost connectport={port}")
    port_dict[device] = port


def devices_forward():
    devices = get_devices()
    port_dict.clear()
    for device in devices:
        device_forward(device, retry=True)
    logging.debug(port_dict)


@app.route('/update')
def update():
    devices_forward()
    return redirect(url_for('index'))


@app.route('/reset')
def reset():
    f.stop()
    for device in get_devices():
        run_cmd(f"adb -s {device} forward --remove-all")
    return 'success'


@app.route('/')
def index():
    s = "there is no device!"
    if port_dict:
        s = (f"{device} <b>[</b>{get_model(device)}<b>]</b> -> <b>{get_addr()}:{port}</b><br>" for device, port in
             port_dict.items())
        s = "\n".join(s)
    return render_template_string("{{ text|safe }}", text=s)


def get_addr():
    global host_addr
    if host_addr is None:
        import socket
        try:
            logging.debug("hostname %s" % socket.gethostname())
            host_name = socket.getfqdn(socket.gethostname())
            logging.debug("qdn %s" % host_name)
            host_addr = socket.gethostbyname(host_name)
        except:
            pass
    logging.debug("IP: %s" % host_addr)
    return host_addr


def notity():
    import notify_center
    import threading
    t = threading.Thread(target=notify_center.notify, daemon=True)
    t.start()


def main():
    notity()
    devices_forward()
    try:
        server = pywsgi.WSGIServer(('0.0.0.0', config.http_port), app)
        server.serve_forever()
    except OSError as e:
        win32api.MessageBox(0, "应用已启动，无需重复启动", "ERROR", win32con.MB_OK)


if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=8888, debug=True)
    main()
