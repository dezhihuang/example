# -*- coding:utf-8 -*-

import sys
import socket
import threading

def threadfun(sock, addr):
    try:
        while True:
            data = sock.recv(1024)
            if data == "quit" or data=="exit":
                print "Client %s exit." % addr[0]
                break
            if data:
                print "Message from %s: %s" % (addr[0],data)
                sock.send("Hello,%s" % data)
        sock.close()
    except socket.errno, e:
        print "Socket error: %s" % str(e)
    except Exception as e:
        print "Other exception: %s" % str(e)
    finally:
        sock.close()

def test_server(port):
    
    # 创建TCP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 启用地址重用
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 绑定地址和端口号
    srv_addr = ("0.0.0.0", port)
    sock.bind(srv_addr)
    
    # 侦听客户端
    sock.listen(5)
    
    while True:
        # 接受客户端连接
        conn, addr = sock.accept()
        t = threading.Thread(target=threadfun, args=(conn, addr))
        t.start()
    
if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = sys.argv[1]
        test_server(int(port))
    else:
        print "Input error."
