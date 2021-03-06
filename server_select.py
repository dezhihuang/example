# -*- coding:utf-8 -*-

import sys
import socket
import select
import signal
import argparse

class ChatServer(object):
    def __init__(self, port, backlog=5):
        self.clients = 0    #客户端数量
        self.clientmap = {} #客户端映射
        self.outputs = []   #输出套接字
        #创建TCP套接字
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #启用地址重用
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #绑定本机地址和端口号
        self.server.bind(("0.0.0.0", port))
        #侦听客户端连接
        self.server.listen(backlog)
        #捕捉用户中断操作
        signal.signal(signal.SIGINT, self.sighandler)
    
    #中断信号处理方法    
    def sighandler(self, signum, frame):
        #关闭所有套接字连接
        for output in self.outputs:
            output.close()
        #关闭服务器
        self.server.close()
        
    def get_client_name(self, client):
        info = self.clientmap[client] #info的内容如：(('127.0.0.1', 56354), 'MyClient')
        host,name = info[0][0],info[1]
        return "@".join((name,host))  #返回内容如：MyClient@127.0.0.1
        
    def run(self):
        inputs = [self.server, sys.stdin]
        self.outputs = []
        running = True
        while running:
            try:
                #开始select监听,对inputs中的服务端server、标准输入stdin进行监听
                #select函数阻塞进程，直到inputs中的套接字被触发（在此例中，套接字接收到客户端发来的握手信号，从而变得可读，满足select函数的“可读”条件），readable返回被触发的套接字（服务器套接字）
                #当再次运行此处时，select再次阻塞进程，同时监听服务器套接字和获得的客户端套接字
                readable,writeable,exceptional = select.select(inputs, self.outputs, [])
            except select.error, e:
                print "Socket error: %s" % str(e)            
            except Exception as e:
                print "Other exception: %s" % str(e)
                break
            
            #循环判断是否有客户端连接进来,当有客户端连接进来时select将触发
            for sock in readable:
                #判断当前触发的是不是服务端对象, 当触发的对象是服务端对象时,说明有新客户端连接进来了
                #如果是服务器套接字被触发（监听到有客户端连接服务器）
                if sock == self.server:   
                    client,address = self.server.accept()
                    print "Chat server: got connection %d from %s" % (client.fileno(), address)
                    
                    cname = client.recv(64).split("NAME: ")[1]                
                    self.clients += 1 #客户端数量加1
                    client.send("CLIENT: "+str(address[0]))
                    inputs.append(client)  #将客户端对象也加入到监听的列表中, 当客户端发送消息时 select 将触发
                    self.clientmap[client] = (address, cname) #客户端映射
                    
                    #向其它客户端发送广播消息
                    msg = "\n(Connected: New client (%d) from %s)" % (self.clients, self.get_client_name(client))
                    for output in self.outputs:
                        output.send(msg)
                    self.outputs.append(client)
                
                elif sock == sys.stdin: #如果是标准输入就发送广播消息
                    junk = sys.stdin.readline().strip()
                    if junk == "exit" or junk=="quit":
                        running = False
                    else:
                        msg = '\n#[Server]>>' + junk
                        for output in self.outputs:
                            if output != sock:
                                output.send(msg)
                                
                else: #由于客户端连接进来时服务端接收客户端连接请求，将客户端加入到了监听列表中(inputs)，客户端发送消息将触发，所以判断是否是客户端对象触发
                    try:
                        data = sock.recv(1024)
                        if data:
                            #向其它客户端发送广播消息
                            msg = '\n#[' + self.get_client_name(sock) + ']>>' + data
                            for output in self.outputs:
                                if output != sock:
                                    output.send(msg)
                        else:
                            #客户端退出，断开连接
                            print "Chat server: %d hung up" % sock.fileno()
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock) #客户端断开连接了，将客户端的监听从inputs列表中移除
                            self.outputs.remove(sock)
                            #发送广播消息告知其它客户端
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
        self.name = name #客户端名称
        self.connected = False
        self.host = host
        self.port = port
        # 初始化提示
        self.prompt = "[" + "@".join((name, socket.gethostname().split(".")[0])) + ']> '
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            self.connected = True
            self.sock.send("NAME: " + self.name) #向服务端发送本客户端名称
            data = self.sock.recv(1024)
            addr = data.split('CLIENT: ')[1] # 客户端IP地址
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
                #开始select监听,对标准输入stdin和客户端套接字进行监听
                #注意：Windows 版本的 Python, select() 函数只能接受 socket, 不接受 File Object, 所以不能 select 标准输入输出.
                readable, writeable,exceptional = select.select([0, self.sock], [], [])
                for sock in readable:
                    if sock == 0:
                        data = sys.stdin.readline().strip() #获取控制台输入，并移除字符串头尾空格字符
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
    
    
     