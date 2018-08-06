import socket
import select
import time
from login_test import settings
import os

class HttpRequest(object):
    """
    用户封装用户请求信息
    """
    def __init__(self, content):
        """

        :param content:用户发送的请求数据：请求头和请求体
        """
        print("content:",content)
        self.content = content

        self.header_bytes = bytes()
        self.body_bytes = bytes()

        self.header_dict = {}

        self.method = ""
        self.url = ""
        self.protocol = ""

        self.initialize()
        self.initialize_headers()

    def initialize(self):

        temp = self.content.split(b'\r\n\r\n', 1)
        print("temp:",temp)
        if len(temp) == 1:# 只有请求头
            self.header_bytes += temp
        else:
            h, b = temp # h:请求头，b：请求体
            self.header_bytes += h
            self.body_bytes += b

    @property
    def header_str(self):# 将字节转化成字符串，方便分割

        return str(self.header_bytes, encoding='utf-8')

    def initialize_headers(self):

        headers = self.header_str.split('\r\n')
        first_line = headers[0].split(' ') # first_line: ['GET', '/', 'HTTP/1.1'] or ['GET', '/favicon.ico', 'HTTP/1.1']
        # print("first_line:",first_line)
        if len(first_line) == 3:
            self.method, self.url, self.protocol = headers[0].split(' ')
            for line in headers:
                kv = line.split(':')
                if len(kv) == 2:
                    k, v = kv
                    self.header_dict[k] = v

# 响应头 响应头 ，回复时用
index_content = '''
HTTP/1.1 200 OK
Content-Type: text/html
\r\n\r\n
'''



test_login_dir = os.path.join(settings.TEMPLATES[0]["DIRS"][0],"test_login.html")
# print(test_login_dir) # G:\Python\login_test\templates\test_login.html
file = open(test_login_dir, 'r',encoding='utf-8')
index_content += file.read()
file.close()


def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 9999,))
    sock.setblocking(False)
    sock.listen(128)

    inputs = []
    inputs.append(sock)

    async_request_dict = {
        # 'socket': futrue
    }

    while True:
        rlist,wlist,elist = select.select(inputs,[],[],0.05)
        for r in rlist:
            if r == sock:
                print("123")
                """新请求到来"""
                conn,addr = sock.accept()
                conn.setblocking(False)
                inputs.append(conn)
            else:
                """客户端发来数据"""
                print("456")

                data = b""
                while True:
                    try:
                        chunk = r.recv(1024)
                        data = data + chunk
                    except Exception as e:
                        chunk = None
                    if not chunk:
                        break

                result = HttpRequest(data)

                r.sendall(bytes(index_content ,encoding='utf-8'))
                # r.sendall(b'HTTP/1.1 200 OK\r\n\r\n<html><body>hello</body></html>')

                inputs.remove(r)
                r.close()



if __name__ == '__main__':
    run()
