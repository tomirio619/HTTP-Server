__author__ = 'S4ndmann'
# handy link : http://stackoverflow.com/questions/24728088/python-parse-http-response-string
# [Errno 9] Bad file descriptor: http://stackoverflow.com/questions/7686275/what-can-lead-to-ioerror-errno-9-bad-file-descriptor-during-os-system
import server
import unittest
import socket
import threading
from httplib import HTTPResponse
import StringIO
import re

class FakeSocket():
    def __init__(self, response_str):
        self._file = StringIO(response_str)
    def makefile(self, *args, **kwargs):
        return self._file


class Test(unittest.TestCase):

    def setUp(self,):
        print '---- setup start'
        self.server=server
        threading.Thread(target=self.serve).start()
        self.client = socket.create_connection(('localhost',8091))
        print '---- setup complete\n'


    def serve(self):
        print '---- preparing server'
        try:
            self.server.main()
            print '---- server online'
        except:
            pass

    def tearDown(self):
        try:
            print('---- closing server')
            self.server.sock.close()
            print('---- server closed')
        except:
            pass

    def test_HTTP200OK(self):
        print '---- testing HTTP 200 OK response'

        message = '''GET /hello_world.gif HTTP/1.1\r\n
		Connection: keep-alive\r\n
		If-None-Match: "686897696a7c876b7e"\r\n\r\n
	     '''

        print '---- sending message'
        self.client.sendall(message)
        response = self.client.recv(1024)
        print '---- response received'
        print response
        print '---- following status code was present'
        statuscode = response[9:15]
        print statuscode

        print '---- end of test'
        self.client.close()
        self.assertEqual("200 OK",statuscode)


    def test_HTTP304NOTMODIFIED(self):
        print '---- testing HTTP 304 NOT MODIFIED response'

        message = '''GET /hello_world.gif HTTP/1.1\r\n
		Connection: keep-alive\r\n
		If-None-Match: "67cd6987484c37bb50e95b8f091bf3c75d230757"\r\n\r\n
	     '''

        print '---- sending message'
        self.client.sendall(message)
        response = self.client.recv(1024)
        print '---- response received'
        print response
        print '---- following status code was present'
        statuscode = response[9:25]
        print statuscode

        print '---- end of test'
        self.client.close()
        self.assertEqual("304 NOT MODIFIED",statuscode)


if __name__ == '__main__':
    unittest.main()