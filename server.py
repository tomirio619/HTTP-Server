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
# By itself, it cannot respond to any actual HTTP requests; it must be subclassed to handle each request method (e.g. GET or POST).
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

    # this function belongs to a thread that will parse the HTTP request and creates an proper response

def timestamp():
    t = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (BaseHTTPRequestHandler.weekdayname[wd], day, BaseHTTPRequestHandler.monthname[month], year, hh, mm, ss)
    return s

def parseMessageFormat(path):
    if path.endswith(".gif"):
        return "image/gif; charset=UTF-8"
    elif path.endswith(".png"):
        return "image/png; charset=UTF-8"
    elif path.endswith("image/jpeg"):
        return "image/jpeg; charset=UTF-8"
    else:
        return "text/html; charset=UTF-8"

def handleRequest(conn,address):
    while True:
        try:
            request=conn.recv(1024)
            if request:
                # parse request
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
                            #zie documentatie, returned iets wat aan pattern voldoet
                            index = request.index("ETag:") + len("ETag:") + 1
                            ETag = request[index:]
                            print "The following ETag is present: %s" %ETag

                            if (ETag == sha1.hexdigest()):
                                print "Both ETag values are the same, sending 304 Not Modified back"
                                header = '''HTTP/1.1 304 NOT MODIFIED\r\nConnection: keep-alive\r\nKeep-Alive: timeout=15\r\nDate: %s\r\nETag:%s\r\nContent-Length: 0\r\n\r\n''' % (timestamp(),sha1.hexdigest())
                                conn.sendall(header)

                            else:
                                print "ETag values were not the same, sending back requested file"
                                #Content-Length: grootte bestand
                                #Content-Type: image/jpg
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

                                #make a new http request, send requested file
                                #op deze manier kunnen we de headers niet maken, want we kunnen geen instantie van BaseHTTPRequesthandler maken
                                #we moeten de headers zelf construeren en deze dan eerst versturen, en dan het bestand.
                                #Data,Server,Size,Content type, error code
                                #in geval van If-None-Match, kijken als etags matchen, zoja niets terugsturen (304 not modified)
                                #zo nee, stuur nieuwe versie bestand terug
                                #indien gevraagd wordt naar directory, stuur index.html
                                #als dit niet bestaat, dan stuur 404 error.


                    else:
                        print 'File doesnt exist'
                        #ook deze headers moeten we zelf maken, kunnen functie schrijven die met parsed_request de headers construeert
                        header= '''HTTP/1.1 404 NOT FOUND\r\nConnection:keep-alive\r\nKeep-Alive:timeout=15\r\nDate:%s\r\nContent-Length: 0\r\n\r\n''' % timestamp()
                        conn.sendall(header)

                else:
                    print 'error %s during parsing, %s' % (parsed_request.error_code, parsed_request.error_message)
                    #send packet back with corresponding error message
                    header = '''HTTP/1.1 %s %s\r\n\r\nContent-Length: 0\r\n\r\n''' (parsed_request.error_code, parsed_request.error_message)
                    conn.sendall(header)

            else:
                print'no more data from', address
                break
        except :
            break
    conn.close()


def main():
    print 'waiting for a connection'

    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = 'localhost'
    port = 8090
    server_address = (address,port)

    print 'starting up on %s port %s' % server_address

    sock.bind(server_address)
    sock.listen(5)

    #Main loop of our server, accepts connections from the outside and let threads handle the requests
    while True:
        connection, client_address = sock.accept()
        t=Thread(target=handleRequest,args=(connection,client_address))
        t.start()

if __name__ == "__main__":
    main()


