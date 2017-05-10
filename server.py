# -*- coding:utf-8 -*-

import sys
import socket
import argparse

def test_server(host, port):
    
    # ����TCP�׽���
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # ���õ�ַ����
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # �󶨵�ַ�Ͷ˿ں�
    srv_addr = (host, port)
    sock.bind(srv_addr)
    
    # �����ͻ���
    sock.listen(5)
    
    while True:
        # ���ܿͻ�������
        client, addr = sock.accept()
        
        # ���ܿͻ�����Ϣ
        data = client.recv(1024)
        if data:
            print "Message from client: %s" % data
            
            # ��ͻ��˷�����Ϣ
            client.send(data)
            
        # �ر�����
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
