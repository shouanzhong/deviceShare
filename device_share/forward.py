import socket
import threading
from log import logging


class ForwardTool(object):
    def __init__(self):
        self.threads_list = []
        self.is_listening = True
        self.socket_list = []
        self.is_running = True

    @staticmethod
    def forward(source, destination):
        while True:
            data = source.recv(1024)
            if len(data) == 0:
                logging.debug(f"已断开: {source}")
                break
            destination.sendall(data)

    def port_forwarding(self, http_port, local_ip, local_port):
        self.is_listening = True
        # 创建本地和远程socket对象
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 绑定本地端口
        server_socket.bind(('0.0.0.0', http_port))
        server_socket.listen(1)
        server_socket.settimeout(60 * 1000)
        # 保存
        self.socket_list.append(server_socket)

        logging.debug(f'正在监听本地端口 {http_port}...')

        while self.is_listening:
            try:
                # 接受远程连接
                remote_conn, local_addr = server_socket.accept()
                logging.debug(f'已接受来自 {local_addr} 的连接')

                # 连接本地服务器
                local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                local_socket.connect((local_ip, local_port))
                logging.debug(f'正在连接到本地服务器 {local_ip}:{local_port}')

                # 创建线程进行数据转发
                t1 = threading.Thread(target=self.forward, args=(remote_conn, local_socket), daemon=True)
                t1.start()
                t1.is_alive()
                t2 = threading.Thread(target=self.forward, args=(local_socket, remote_conn), daemon=True)
                t2.start()
                logging.debug("启动两个线程...")
            except OSError:
                logging.debug("socket 可能已关闭")
            finally:
                pass

    def ports_forward(self, *ports):
        logging.debug("ports: %s" % ports)
        ports_exist = (int(t.getName().strip()) for t in self.threads_list)
        port_unit = set(ports) - set(ports_exist)
        for port in port_unit:
            t = threading.Thread(target=self.port_forwarding, args=(port, "localhost", port), daemon=True, name=str(port))
            t.start()
            self.threads_list.append(t)

    def stop(self):
        self.is_listening = False
        #
        for sock in self.socket_list:
            sock.close()
        self.socket_list.clear()
        #
        for t in self.threads_list:
            t.join()
        self.threads_list.clear()

    def __del__(self):
        print("clear")
        self.stop()


if __name__ == '__main__':
    local_port = [9999, ]  # 本地端口
    # remote_ip = 'localhost'  # 远程服务器IP
    # remote_port = 9999  # 远程服务器端口
    a = ForwardTool()
    a.ports_forward(*local_port)
    print(a.socket_list)
    print("finish")
