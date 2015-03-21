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
import re
from timeit import default_timer

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
    if path.endswith(".gif"):
        return "image/gif; charset=UTF-8"
    elif path.endswith(".png"):
        return "image/png; charset=UTF-8"
    elif path.endswith(".jpeg"):
        return "image/jpeg; charset=UTF-8"
    elif path.endswith(".jpg"):
        return "image/jpg; charset=UTF-8"
    elif path.endswith(".BMP"):
        return "image/bmp; charset=UTF-8"
    elif path.endswith(".bmp"):
        return "image/bmp; charset=UTF-8"
    else:
        return "text/html; charset=UTF-8"


# A thread will be dispatched to handle the client that connects to the server.
# It will parse the request (using the HTTPRequest class) and send a response.
# Both the address and the socket will be passed to this method, so that the thread can send data over this socket
def handleRequest(conn, address):
    starttime = default_timer()
    timeout = 5
    while True:
        try:
            request = conn.recv(1024)
            if request:
                parsed_request = HTTPRequest(request)
                starttime = default_timer()

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
                            ETag = ((unparsedETag.split('\r\n'))[0]).replace('''"''',"")       #split at the \r\n and remove the two quotes surrounding the ETag
                            print ETag
                            print sha1.hexdigest()
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
                                             % (
                                        parseMessageFormat(parsed_request.path), timestamp(), os.path.getsize(path),
                                        sha1.hexdigest())
                                    conn.sendall(header)
                                    conn.sendall(f.read())
                                    conn.close()
                                    break

                                else:
                                    header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection: keep-alive\r\nKeep-Alive: timeout=%i\r\nDate:%s\r\nContent-Length: %i\r\nETag:"%s"\r\n\r\n''' \
                                             % (parseMessageFormat(parsed_request.path), timeout, timestamp(),
                                                os.path.getsize(path), sha1.hexdigest())
                                    conn.sendall(header)
                                    conn.sendall(f.read())

                        else:
                            f = open(path, 'rb')

                            if parsed_request.close_connection:
                                header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection: close\r\nDate:%s\r\nContent-Length: %i\r\nETag:"%s"\r\n\r\n''' \
                                         % (parseMessageFormat(parsed_request.path), timestamp(), os.path.getsize(path),
                                            sha1.hexdigest())
                                conn.sendall(header)
                                conn.sendall(f.read())
                                conn.close()
                                break

                            else:
                                header = '''HTTP/1.1 200 OK\r\nContent-Type: %s\r\nConnection: keep-alive\r\nKeep-Alive: timeout=%i\r\nDate:%s\r\nContent-Length: %i\r\nETag:"%s"\r\n\r\n''' \
                                         % (parseMessageFormat(parsed_request.path), timeout, timestamp(),
                                            os.path.getsize(path), sha1.hexdigest())
                                conn.sendall(header)
                                conn.sendall(f.read())


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
                time_waited = int(default_timer() - starttime)
                if time_waited >= timeout:
                    conn.close()
                    print 'timeout ', address
                    break
        except:
            time_waited = default_timer() - starttime
            if int(time_waited) >= timeout:
                conn.close()
                print 'timeout ', address
                break
            else:
                pass


# The main function of the HTTPServer.
# A socket will be created on the specified address and port.
# The server will accept incoming connections and spawn a thread that will handle the requests for that client.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def main():
    address = 'localhost'
    port = 8091
    server_address = (address, port)
    sock.bind(server_address)
    sock.listen(5)
    while True:
        connection, client_address = sock.accept()
        t = Thread(target=handleRequest, args=(connection, client_address))
        t.start()


if __name__ == "__main__":
    main()


