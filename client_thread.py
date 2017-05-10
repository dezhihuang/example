# -*- coding:utf-8 -*-

import sys
import socket
import argparse

def test_client(host, port):
    
    # ����TCP�׽���
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # ���ӷ�����
    srv_addr = (host, port)
    sock.connect(srv_addr)
    
    # ���Ͳ���������
    try:
        # ������Ϣ
        while True:          
            msg = raw_input("Please nput:")
            sock.sendall(msg)
            
            if msg=="quit" or msg=="exit":
                break            
            
            # ������Ϣ
            data = sock.recv(1024)
            print "Message from server: %s" % data
        sock.close()
    except socket.errno, e:
        print "Socket error: %s" % str(e)
    except Exception as e:
        print "Other exception: %s" % str(e)
    finally:
        sock.close()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Socket Server Example")
    parser.add_argument("--ip", action="store", dest="host", type=str, required=True)
    parser.add_argument("--port", action="store", dest="port", type=int, required=True)
    given_args = parser.parse_args()
    host = given_args.host
    port = given_args.port
    test_client(host, port)        
        
                
