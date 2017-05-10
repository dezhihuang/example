# -*- coding:utf-8 -*-

import sys
import socket
import argparse

def test_server(host, port):
    
    # 创建TCP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 启用地址重用
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 绑定地址和端口号
    srv_addr = (host, port)
    sock.bind(srv_addr)
    
    # 侦听客户端
    sock.listen(5)
    
    while True:
        # 接受客户端连接
        client, addr = sock.accept()
        
        # 接受客户端消息
        data = client.recv(1024)
        if data:
            print "Message from client: %s" % data
            
            # 向客户端发送消息
            client.send(data)
            
        # 关闭连接
        client.close()
    
if __name__ == "__main__":
    '''
    parser = argparse.ArgumentParser(description="Socket Server Example")
    parser.add_argument("--port", action="store", dest="port", type=int, required=True)
    parser.add_argument("--ip", action="store", dest="host", type=str, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    host = given_args.host
    test_server(host, port)
    '''
    if len(sys.argv) == 2:
        host = "127.0.0.1"
        port = sys.argv[1]
        test_server(host, int(port))
    elif len(sys.argv) == 3:
        host = sys.argv[1]
        port = sys.argv[2]
        test_server(host, int(port))
    else:
        print "Input error."
