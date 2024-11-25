import socket
import logging

from device_share import config

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s-%(levelname)s] %(message)s')


# 创建一个 socket 对象
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 获取本地主机名和端口号
host = socket.gethostname()
port = 12345

# 绑定主机名和端口号
server_socket.bind(("0.0.0.0", port))

# 设置最大连接数
server_socket.listen(1)


while True:
    logging.debug('等待客户端连接...')
    # 建立客户端连接
    client_socket, addr = server_socket.accept()

    logging.info('连接地址：%s %s' % addr)
    logging.info(f"服务器地址：http://{addr[0]}:{config.http_port}")

    # 接收客户端发送的数据
    data = client_socket.recv(1024).decode()
    logging.info('%s：%s' % (addr[0], data))

    # 发送响应给客户端
    response = 'OK'
    client_socket.send(response.encode())

    # 关闭连接
    client_socket.close()
    logging.info("over ")

