#!/usr/bin/python
__author__ = 'Justin Mol (s4386094) & Tom Sandmann (s4330048)'

import socket
import hashlib
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
import os.path
import time
import mimetypes
import select


# BaseHTTPRequestHandler is used to handle the HTTP requests that arrive at the server.
# By itself, it cannot respond to any actual HTTP requests.
# It must be subclassed to handle each request method (e.g. GET or POST).
# BaseHTTPRequestHandler provides a number of class and instance variables, and methods for use by subclasses.
# close_connection = 1 if close is the value of the header Connection, otherwise it has the value 0.


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.default_request_version = "HTTP/1.1"
        self.request_version = "HTTP/1.1"
        self.parse_request()
        # determine if the connection has to closed or not
        if "Connection: close" in request_text:
            self.close_connection = 1
        else:
            self.close_connection = 0

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message


# Generates a timestamp according to the HTTP standard
def timestamp():
    t = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        BaseHTTPRequestHandler.weekdayname[wd], day, BaseHTTPRequestHandler.monthname[month], year, hh, mm, ss)
    return s


# Given the path of a request, it will determine the Content-Type of the response
def parseMessageFormat(path):
    return mimetypes.guess_type(path)[0]


# A thread will be dispatched to handle the client that connects to the server.
# It will parse the request (using the HTTPRequest class) and send a response.
# Both the address and the socket will be passed to this method, so that the thread can send data over this socket
def handleRequest(conn, address):
    timeout = 5
    print 'thread started for %s %s' % address
    while True:
        try:
            ready_to_read, ready_to_write, in_error = select.select([conn], [], [], 5)
            if len(ready_to_read)+len(ready_to_write)+len(in_error) == 0:
                print 'Connection Timed Out'
                conn.close()
                break
            elif len(ready_to_read) > 0:
                request = conn.recv(1024)
                parsed_request = HTTPRequest(request)

                if parsed_request.error_code is None:
                    path = "content" + parsed_request.path

                    if os.path.isfile(path):
                        f = open(path, 'r')
                        sha1 = hashlib.sha1()
                        try:
                            sha1.update(f.read())
                        finally:
                            f.close()

                        if "If-None-Match:" in request:
                            index = request.index("If-None-Match:") + len("If-None-Match:") + 1
                            unparsedETag = request[index:]
                            ETag = ((unparsedETag.split('\r\n'))[0]).replace('''"''', "")
                            if ETag == sha1.hexdigest():
                                if parsed_request.close_connection:
                                    header = '''HTTP/1.1 304 NOT MODIFIED\r\nConnection: close\r\nDate: %s\r\nETag:"%s"\r\nContent-Length: 0\r\n\r\n''' \
                                             % (timestamp(), sha1.hexdigest())
                                    conn.sendall(header)
                                    conn.close()
                                    break

                                else:
                                    header = '''HTTP/1.1 304 NOT MODIFIED\r\nConnection: keep-alive\r\nKeep-Alive: timeout=%i\r\nDate: %s\r\nETag:"%s"\r\nContent-Length: 0\r\n\r\n''' \
                                             % (timeout, timestamp(), sha1.hexdigest())
                                    conn.sendall(header)

                            else:
                                f = open(path, 'rb')

                                if parsed_request.close_connection:
                                    header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection: close\r\nDate:%s\r\nContent-Length: %i\r\nETag:"%s"\r\n\r\n''' \
                                             % (parseMessageFormat(path), timestamp(), os.path.getsize(path), sha1.hexdigest())
                                    conn.sendall(header + f.read())
                                    conn.close()
                                    break

                                else:
                                    header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection: keep-alive\r\nKeep-Alive: timeout=%i\r\nDate:%s\r\nContent-Length: %i\r\nETag:"%s"\r\n\r\n''' \
                                             % (parseMessageFormat(path), timeout, timestamp(),
                                                os.path.getsize(path), sha1.hexdigest())
                                    conn.sendall(header + f.read())

                        else:

                            f = open(path, 'rb')

                            if parsed_request.close_connection:
                                header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection: close\r\nDate:%s\r\nContent-Length: %i\r\nETag:"%s"\r\n\r\n''' \
                                         % (parseMessageFormat(path), timestamp(), os.path.getsize(path),
                                            sha1.hexdigest())
                                conn.sendall(header + f.read())
                                conn.close()
                                break

                            else:
                                header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection: keep-alive\r\nKeep-Alive: timeout=%i\r\nDate:%s\r\nContent-Length: %i\r\nETag:"%s"\r\n\r\n''' \
                                         % (parseMessageFormat(path), timeout, timestamp(),
                                            os.path.getsize(path), sha1.hexdigest())
                                conn.sendall(header + f.read())

                    else:
                        value = False
                        try:
                            value = os.path.isdir(path)
                        except:
                            pass

                        if value:
                            if os.path.isfile(path+"index.html"):
                                location = path + "index.html"
                                f = open(location, 'rb')
                                sha1 = hashlib.sha1()
                                sha1.update(f.read())
                                f.close()
                                f = open(location, 'rb')
                                if parsed_request.close_connection:
                                    header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection:close\r\nDate:%s\r\nContent-Length: %i\r\nETag:"%s"\r\n\r\n''' \
                                             % (parseMessageFormat(location), timestamp(), os.path.getsize(location), sha1.hexdigest())
                                    conn.sendall(header + f.read())
                                    conn.close()
                                    break

                                else:
                                    header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection:keep-alive\r\nKeep-Alive:timeout=%i\r\nDate:%s\r\nContent-Length: %i\r\nETag:"%s"\r\n\r\n''' \
                                             % (parseMessageFormat(location), timeout, timestamp(), os.path.getsize(location), sha1.hexdigest())
                                    conn.sendall(header + f.read())

                            else:
                                if parsed_request.close_connection:
                                    header = '''HTTP/1.1 404 NOT FOUND\r\nConnection:close\r\nDate:%s\r\nContent-Length: 0\r\n\r\n''' % timestamp()
                                    conn.sendall(header)
                                    conn.close()
                                    break

                                else:
                                    header = '''HTTP/1.1 404 NOT FOUND\r\nConnection:keep-alive\r\nKeep-Alive:timeout=%i\r\nDate:%s\r\nContent-Length: 0\r\n\r\n''' \
                                             % (timeout, timestamp())
                                    conn.sendall(header)

                        else:
                            if parsed_request.close_connection:
                                header = '''HTTP/1.1 404 NOT FOUND\r\nConnection:close\r\nDate:%s\r\nContent-Length: 0\r\n\r\n''' % timestamp()
                                conn.sendall(header)
                                conn.close()
                                break

                            else:
                                header = '''HTTP/1.1 404 NOT FOUND\r\nConnection:keep-alive\r\nKeep-Alive:timeout=%i\r\nDate:%s\r\nContent-Length: 0\r\n\r\n''' \
                                         % (timeout, timestamp())
                                conn.sendall(header)

                        if parsed_request.close_connection:
                            header = '''HTTP/1.1 404 NOT FOUND\r\nConnection:close\r\nDate:%s\r\nContent-Length: 0\r\n\r\n''' % timestamp()
                            conn.sendall(header)
                            conn.close()
                            break

                        else:
                            header = '''HTTP/1.1 404 NOT FOUND\r\nConnection:keep-alive\r\nKeep-Alive:timeout=%i\r\nDate:%s\r\nContent-Length: 0\r\n\r\n''' \
                                     % (timeout, timestamp())
                            conn.sendall(header)

                else:
                    if parsed_request.close_connection:
                        header = '''HTTP/1.1 %s %s\r\nConnection: close\r\nContent-Length: 0\r\n\r\n''' % (
                            parsed_request.error_code, parsed_request.error_message)
                        conn.sendall(header)
                        conn.close()
                        break

                    else:
                        header = '''HTTP/1.1 %s %s\r\n\Connection: keep-alive\r\nKeep-Alive:timeout=%i\r\nContent-Length: 0\r\n\r\n''' \
                                 % (parsed_request.error_code, parsed_request.error_message, timeout)
                        conn.sendall(header)

            else:
                pass
        except:
            print 'Connection Timed Out, closing connection'
            conn.close()
            break


# The main function of the HTTPServer.
# A socket will be created on the specified address and port.
# The server will accept incoming connections and spawn a thread that will handle the requests for that client.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 8090


def main():
    print 'starting server'
    address = 'localhost'
    server_address = (address, port)
    sock.bind(server_address)
    sock.listen(5)
    while True:
        connection, client_address = sock.accept()
        t = Thread(target=handleRequest, args=(connection, client_address))
        t.start()

if __name__ == "__main__":
    main()