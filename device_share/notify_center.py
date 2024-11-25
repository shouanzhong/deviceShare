from log import logging
import socket
import time
import config


# 获取服务器的主机名和端口号
from device_share import get_devices


def notify():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    for i in range(100):
        try:
            client_socket.connect((config.host, config.port))
            break
        except:
            logging.debug("wait for server...")
            time.sleep(2)

    devices = get_devices()
    message = str(list(enumerate(devices)))
    client_socket.send(message.encode())

    response = client_socket.recv(1024).decode()
    logging.debug('server：%s' % response)

    client_socket.close()


if __name__ == '__main__':
    notify()