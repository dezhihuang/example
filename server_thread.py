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
    
    # ����TCP�׽���
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # ���õ�ַ����
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # �󶨵�ַ�Ͷ˿ں�
    srv_addr = ("0.0.0.0", port)
    sock.bind(srv_addr)
    
    # �����ͻ���
    sock.listen(5)
    
    while True:
        # ���ܿͻ�������
        conn, addr = sock.accept()
        t = threading.Thread(target=threadfun, args=(conn, addr))
        t.start()
    
if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = sys.argv[1]
        test_server(int(port))
    else:
        print "Input error."
