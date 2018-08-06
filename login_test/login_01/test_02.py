import socket
import select
import time

"""
异步非阻塞框架（服务端）：
  设置 future = Future()，通过Future实现异步非阻塞
      1. 当设置 future = Future()时，挂起当前请求，线程可以处理其他请求 
      2. 当给future设置值时，当前挂起的请求返回
"""

class HttpRequest(object):
    """
    用户封装用户请求信息
    """
    def __init__(self, content):
        """

        :param content:用户发送的请求数据：请求头和请求体
        """
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
        if len(temp) == 1:
            self.header_bytes += temp[0]
        else:
            h, b = temp
            self.header_bytes += h
            self.body_bytes += b

    @property
    def header_str(self):
        return str(self.header_bytes, encoding='utf-8')

    def initialize_headers(self):
        headers = self.header_str.split('\r\n')
        first_line = headers[0].split(' ')
        if len(first_line) == 3:
            self.method, self.url, self.protocol = headers[0].split(' ')
            for line in headers:
                kv = line.split(':')
                if len(kv) == 2:
                    k, v = kv
                    self.header_dict[k] = v

class Future(object):
    def __init__(self):
        self.result = None
F = Future()
def main(request):
    global F
    return F # Future对象

def stop(request):
    global F
    F.result = b"xxxxxxxxxxxxx"
    return "stop"


def index(request):

    return "indexasdfasdfasdf"


routers = [
    ('/main/',main),
    ('/index/',index),
    ('/stop/',stop),
]

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
                """新请求到来"""
                conn,addr = sock.accept()
                conn.setblocking(False)
                inputs.append(conn)
            else:
                """客户端发来数据"""
                data = b""
                while True:
                    try:
                        chunk = r.recv(1024)
                        data = data + chunk
                    except Exception as e:
                        chunk = None
                    if not chunk:
                        break
                # data进行处理：请求头和请求体
                request = HttpRequest(data)
                # 1. 请求头中获取url
                # 2. 去路由中匹配，获取指定的函数
                # 3. 执行函数，获取返回值
                # 4. 将返回值 r.sendall(b'alskdjalksdjf;asfd')
                import re
                flag = False
                func = None
                for route in routers:
                    if re.match(route[0],request.url):
                        print(route[0],request.url)
                        flag = True
                        func = route[1]
                        break
                if flag: # url路径匹配成功
                    result = func(request) # 执行函数
                    if isinstance(result,Future):# 判断是否Future对象，如是则挂起不执行，否则执行服务端响应操作
                        async_request_dict[r] = result
                    else:
                        r.sendall(b'HTTP/1.1 200 OK\r\n\r\n<html><body>hello</body></html>')
                        inputs.remove(r)
                        r.close()
                else:# 匹配不成功，返回404错误
                    r.sendall(b"HTTP/1.1 200 OK\r\n\r\n<html><body>404</body></html>")
                    inputs.remove(r)
                    r.close()


        for conn in list(async_request_dict.keys()):# 当Future函数中result有值，才执行。实现可控制的异步非阻塞操作
            future = async_request_dict[conn]
            if future.result:
                conn.sendall(b'HTTP/1.1 200 OK\r\n\r\n<html><body>hello</body></html>')
                conn.close()
                del async_request_dict[conn]
                inputs.remove(conn)

if __name__ == '__main__':
    run()