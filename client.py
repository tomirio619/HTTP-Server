#!/usr/bin/python
import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8090)
print 'connecting to %s port %s' % server_address

try:
    sock.connect(server_address)
    message1 = '''GET /hello_world.gif HTTP/1.1\r\n
		Host: [rsid].112.2o7.net\r\n
		Connection: keep-alive\r\n
		If-None-Match: "686897696a7c876b7e"\r\n\r\n
	     '''
    message2 = '''GET /hello_world.gif HTTP/1.1\r\n
		Host: [rsid].112.2o7.net\r\n
		Connection: close\r\n
		If-None-Match: "686897696a7c876b7e"\r\n\r\n
	     '''
    message=message2
    print 'sending "%s"' % message
    sock.sendall(message)
    amount_received = 0
    amount_expected = len(message)

    while True:
        try:
            data = sock.recv(1024)
            amount_received += len(data)
            if data:
                print 'received "%s"' % data
        except:
            print 'waiting for time out'
            break
except:
    print 'server offline'