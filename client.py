#!/usr/bin/python
import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 8090)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    
    # Send data
    message = '''GET /hello_world.gif HTTP/1.1\r\n
		Host: [rsid].112.2o7.net\r\n
		Keep-Alive: timeout=15\r\n
		Connection: keep-alive\r\n
		X-Forwarded-For: 192.168.10.1\r\n
		ETag: 686897696a7c876b7e\r\n
		\r\n
	     '''

    print >>sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(1024)
        amount_received += len(data)
        print >>sys.stderr, 'received "%s"' % data

finally:
    print 'closing socket'
    sock.close()
