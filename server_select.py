# -*- coding:utf-8 -*-

import sys
import socket
import select
import signal
import argparse

class ChatServer(object):
    def __init__(self, port, backlog=5):
        self.clients = 0    #�ͻ�������
        self.clientmap = {} #�ͻ���ӳ��
        self.outputs = []   #����׽���
        #����TCP�׽���
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #���õ�ַ����
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #�󶨱�����ַ�Ͷ˿ں�
        self.server.bind(("0.0.0.0", port))
        #�����ͻ�������
        self.server.listen(backlog)
        #��׽�û��жϲ���
        signal.signal(signal.SIGINT, self.sighandler)
    
    #�ж��źŴ�����    
    def sighandler(self, signum, frame):
        #�ر������׽�������
        for output in self.outputs:
            output.close()
        #�رշ�����
        self.server.close()
        
    def get_client_name(self, client):
        info = self.clientmap[client] #info�������磺(('127.0.0.1', 56354), 'MyClient')
        host,name = info[0][0],info[1]
        return "@".join((name,host))  #���������磺MyClient@127.0.0.1
        
    def run(self):
        inputs = [self.server, sys.stdin]
        self.outputs = []
        running = True
        while running:
            try:
                #��ʼselect����,��inputs�еķ����server����׼����stdin���м���
                #select�����������̣�ֱ��inputs�е��׽��ֱ��������ڴ����У��׽��ֽ��յ��ͻ��˷����������źţ��Ӷ���ÿɶ�������select�����ġ��ɶ�����������readable���ر��������׽��֣��������׽��֣�
                #���ٴ����д˴�ʱ��select�ٴ��������̣�ͬʱ�����������׽��ֺͻ�õĿͻ����׽���
                readable,writeable,exceptional = select.select(inputs, self.outputs, [])
            except select.error, e:
                print "Socket error: %s" % str(e)            
            except Exception as e:
                print "Other exception: %s" % str(e)
                break
            
            #ѭ���ж��Ƿ��пͻ������ӽ���,���пͻ������ӽ���ʱselect������
            for sock in readable:
                #�жϵ�ǰ�������ǲ��Ƿ���˶���, �������Ķ����Ƿ���˶���ʱ,˵�����¿ͻ������ӽ�����
                #����Ƿ������׽��ֱ��������������пͻ������ӷ�������
                if sock == self.server:   
                    client,address = self.server.accept()
                    print "Chat server: got connection %d from %s" % (client.fileno(), address)
                    
                    cname = client.recv(64).split("NAME: ")[1]                
                    self.clients += 1 #�ͻ���������1
                    client.send("CLIENT: "+str(address[0]))
                    inputs.append(client)  #���ͻ��˶���Ҳ���뵽�������б���, ���ͻ��˷�����Ϣʱ select ������
                    self.clientmap[client] = (address, cname) #�ͻ���ӳ��
                    
                    #�������ͻ��˷��͹㲥��Ϣ
                    msg = "\n(Connected: New client (%d) from %s)" % (self.clients, self.get_client_name(client))
                    for output in self.outputs:
                        output.send(msg)
                    self.outputs.append(client)
                
                elif sock == sys.stdin: #����Ǳ�׼����ͷ��͹㲥��Ϣ
                    junk = sys.stdin.readline().strip()
                    if junk == "exit" or junk=="quit":
                        running = False
                    else:
                        msg = '\n#[Server]>>' + junk
                        for output in self.outputs:
                            if output != sock:
                                output.send(msg)
                                
                else: #���ڿͻ������ӽ���ʱ����˽��տͻ����������󣬽��ͻ��˼��뵽�˼����б���(inputs)���ͻ��˷�����Ϣ�������������ж��Ƿ��ǿͻ��˶��󴥷�
                    try:
                        data = sock.recv(1024)
                        if data:
                            #�������ͻ��˷��͹㲥��Ϣ
                            msg = '\n#[' + self.get_client_name(sock) + ']>>' + data
                            for output in self.outputs:
                                if output != sock:
                                    output.send(msg)
                        else:
                            #�ͻ����˳����Ͽ�����
                            print "Chat server: %d hung up" % sock.fileno()
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock) #�ͻ��˶Ͽ������ˣ����ͻ��˵ļ�����inputs�б����Ƴ�
                            self.outputs.remove(sock)
                            #���͹㲥��Ϣ��֪�����ͻ���
                            msg = "\n(Now hung up: Client from %s)" % self.get_client_name(sock)
                            for output in self.outputs:
                                output.send(msg)
                    except socket.error, e:
                        inputs.remove(sock)
                        self.outputs.remove(sock)
                        print "Socket error: %s" % str(e)
                    except Exception as e:
                        inputs.remove(sock)
                        self.outputs.remove(sock)
                        print "Other exception: %s" % str(e)    
                                                
        self.server.close()                
 
 
class ChatClient(object):
    def __init__(self, name, port, host="127.0.0.1"):
        self.name = name #�ͻ�������
        self.connected = False
        self.host = host
        self.port = port
        # ��ʼ����ʾ
        self.prompt = "[" + "@".join((name, socket.gethostname().split(".")[0])) + ']> '
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            self.connected = True
            self.sock.send("NAME: " + self.name) #�����˷��ͱ��ͻ�������
            data = self.sock.recv(1024)
            addr = data.split('CLIENT: ')[1] # �ͻ���IP��ַ
            self.prompt = '[' + '@'.join((self.name, addr)) + ']> '
        except socket.error,e:
            print "Failed to connect to chat server @ port %d" % self.port
            sys.exit(1)
        except Exception as e:
            print "Other exception: %s" % str(e) 
            sys.exit(1)
    
    def run(self):
        while self.connected:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()
                #��ʼselect����,�Ա�׼����stdin�Ϳͻ����׽��ֽ��м���
                #ע�⣺Windows �汾�� Python, select() ����ֻ�ܽ��� socket, ������ File Object, ���Բ��� select ��׼�������.
                readable, writeable,exceptional = select.select([0, self.sock], [], [])
                for sock in readable:
                    if sock == 0:
                        data = sys.stdin.readline().strip() #��ȡ����̨���룬���Ƴ��ַ���ͷβ�ո��ַ�
                        if data: 
                            self.sock.send(data)
                    elif sock == self.sock:
                        data = self.sock.recv(1024)
                        if not data:
                            print 'Client shutting down.'
                            self.connected = False
                            break
                        else:
                            sys.stdout.write(data + '\n')
                            sys.stdout.flush()
            except KeyboardInterrupt:
                print " Client interrupted. """
                self.sock.close()
                break
            except Exception as e:
                print "Other exception: %s" % str(e) 
                self.sock.close()
                break                
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Socket Server Example with Select')
    parser.add_argument('--name', action="store", dest="name", required=True)
    parser.add_argument('--ip', action="store", dest="host", required=True)
    parser.add_argument('--port', action="store", dest="port", type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    name = given_args.name
    host = given_args.host
    if name.upper() == "SERVER":
        server = ChatServer(port)
        server.run()
    else:
        client = ChatClient(name=name, port=port, host=host)
        client.run()    
    
    
     