#!/usr/bin/python
import socket
import sys
import BaseHTTPServer
import hashlib
from threading import Thread
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
import os.path
import time


# BaseHTTPRequestHandler is used to handle the HTTP requests that arrive at the server.
# By itself, it cannot respond to any actual HTTP requests.
# It must be subclassed to handle each request method (e.g. GET or POST).
# BaseHTTPRequestHandler provides a number of class and instance variables, and methods for use by subclasses.
class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.request_version="HTTP/1.1"
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):

        self.error_code = code
        self.error_message = message

#Generates a timestamp according to the HTTP standard
def timestamp():
    t = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (BaseHTTPRequestHandler.weekdayname[wd], day, BaseHTTPRequestHandler.monthname[month], year, hh, mm, ss)
    return s

# Given the path of an request, it will determine the Content-Type of the response
def parseMessageFormat(path):
    if path.endswith(".gif"):
        return "image/gif; charset=UTF-8"
    elif path.endswith(".png"):
        return "image/png; charset=UTF-8"
    elif path.endswith("image/jpeg"):
        return "image/jpeg; charset=UTF-8"
    else:
        return "text/html; charset=UTF-8"

# A thread will be dispatched to handle the client that connects to the server.
# It will parse the request (using the HTTPRequest class) and send a response.
# Both the address and the socket will be passed to this method, so that the thread can send data over this socket
def handleRequest(conn,address):
    while True:
        try:
            request=conn.recv(1024)
            if request:
                parsed_request = HTTPRequest(request)
                print 'Checking if there was an error during parsing the request'

                if parsed_request.error_code == None:
                    print 'No parse error during parsing'
                    print 'We check if the path exists'
                    path = "content" +  parsed_request.path
                    print "het gevraagde pad is %s" %path
                    path = "content" +  parsed_request.path

                    if os.path.isfile(path):
                        print 'File exists, sending file back'
                        f = open(path, 'r')
                        sha1 = hashlib.sha1()
                        try:
                            sha1.update(f.read())
                        finally:
                            f.close()
                        print "we zoeken als Etag in message zit:"

                        if ("ETag:" in request):
                            index = request.index("ETag:") + len("ETag:") + 1
                            ETag = request[index:]
                            print "The following ETag is present: %s" %ETag

                            if (ETag == sha1.hexdigest()):
                                print "Both ETag values are the same, sending 304 Not Modified back"
                                header = '''HTTP/1.1 304 NOT MODIFIED\r\nConnection: keep-alive\r\nKeep-Alive: timeout=15\r\nDate: %s\r\nETag:%s\r\nContent-Length: 0\r\n\r\n''' % (timestamp(),sha1.hexdigest())
                                conn.sendall(header)

                            else:
                                print "ETag values were not the same, sending back requested file"
                                f = open(path, 'rb')
                                print 'de grootte van het bestand is %i' %os.path.getsize(path)
                                header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection:keep-alive\r\nKeep-Alive:timeout=15\r\nDate:%s\r\nContent-Length: %i\r\n\r\n''' % (parseMessageFormat(parsed_request.path),timestamp(),os.path.getsize(path))
                                conn.sendall(header)
                                conn.sendall(f.read())

                        else:
                            print "No ETag value present, sending back response"
                            f = open(path, 'rb')
                            print 'de grootte van het bestand is %i' %os.path.getsize(path)
                            header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection:keep-alive\r\nKeep-Alive:timeout=15\r\nDate:%s\r\nContent-Length: %i\r\n\r\n''' % (parseMessageFormat(parsed_request.path),timestamp(),os.path.getsize(path))
                            conn.sendall(header)
                            conn.sendall(f.read())

                    else:
                        print 'File doesnt exist'
                        header= '''HTTP/1.1 404 NOT FOUND\r\nConnection:keep-alive\r\nKeep-Alive:timeout=15\r\nDate:%s\r\nContent-Length: 0\r\n\r\n''' % timestamp()
                        conn.sendall(header)

                else:
                    print 'error %s during parsing, %s' % (parsed_request.error_code, parsed_request.error_message)
                    header = '''HTTP/1.1 %s %s\r\n\r\nContent-Length: 0\r\n\r\n''' (parsed_request.error_code, parsed_request.error_message)
                    conn.sendall(header)

            else:
                print'no more data from', address
                break
        except:
            break
    conn.close()

# The main function of the HTTPServer.
# A socket will be created on the specified address and port.
# The server will accept incoming connections and spawn a thread that will handle the requests for that client.
def main():
    print 'waiting for a connection'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = 'localhost'
    port = 8090
    server_address = (address, port)
    print 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    sock.listen(5)
    while True:
        connection, client_address = sock.accept()
        t=Thread(target=handleRequest,args=(connection,client_address))
        t.start()

if __name__ == "__main__":
    main()


