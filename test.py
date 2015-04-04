#!/usr/bin/python
__author__ = 'Justin Mol (s4386094) & Tom Sandmann (s4330048)'

# Configure the tests in pycharm:
# Druk op shift+alt+F10 (Run/Debug Configurations)
# Selecteer uit het drop down menu "Edit Configurations"
# Druk links bovenin op het + en selecteer Python tests->Unittests.
# Selecteer als "Script:" test.py , geef het geheel een naam (b.v. ServerTests) en druk op apply en op OK
# Klik rechtsboven, links naast de groene play knop, op het dropdown menu en selecteer de naam die je hebt ingevoerd.
# Druk nu op het groene play knopje en als het goed is verschijnt er nu een interface waarin alle tests worden uitgevoerd.

import server
import unittest
import socket
import time


class Test(unittest.TestCase):

    def setUp(self,):
        print '---- setup start'
        self.server = server
        self.client = socket.create_connection(('localhost', server.port))
        print '---- setup complete\n'

    def tearDown(self):
        print('---- closing client connection')
        self.client.close()
        print('---- client connection is closed')

    def test_HTTP200OK(self):
        print '---- testing HTTP 200 OK response'

        message = '''GET /hello_world.gif HTTP/1.1\r\n
        Connection: close\r\n
        If-None-Match: "686897696a7c876b7e"\r\n\r\n'''

        print '---- sending message'
        self.client.sendall(message)
        response = self.client.recv(1024)
        print '---- response received'
        print response
        print '---- following status code was present'
        statuscode = response[9:15]
        print statuscode

        print '---- end of test'
        self.assertEqual("200 OK", statuscode)

    def test_HTTP304NOTMODIFIED(self):
        print '---- testing HTTP 304 NOT MODIFIED response'

        message1 = '''GET /hello_world.gif HTTP/1.1\r\n
        Connection: keep-alive\r\n\r\n'''

        message2 = '''GET /hello_world.gif HTTP/1.1\r\n
        Connection: close\r\n
        If-None-Match: "67cd6987484c37bb50e95b8f091bf3c75d230757"\r\n\r\n'''

        print '---- sending message'
        self.client.sendall(message1)
        response1 = self.client.recv(888888)

        self.client.sendall(message2)
        response2 = self.client.recv(888888)
        print '---- response received'
        print '---- following status code was present'
        statuscode = response2[9:25]
        print statuscode

        print '---- end of test'
        self.assertEqual("304 NOT MODIFIED", statuscode)

    def test_HTTP404FILENOTFOUND(self):
        print '---- testing HTTP 404 NOT FOUND response for file'

        message = '''GET /haiio_world.gif HTTP/1.1\r\n
        Connection: close\r\n\r\n'''

        print '---- sending message'
        self.client.sendall(message)
        response = self.client.recv(1024)
        print '---- response received'
        print response
        print '---- following status code was present'
        statuscode = response[9:22]
        print statuscode

        print '---- end of test'
        self.assertEqual("404 NOT FOUND", statuscode)

    def test_HTTP404PAGENOTFOUND(self):
        print '---- testing HTTP 404 NOT FOUND response for index.html'

        message = '''GET /mp3.html HTTP/1.1\r\n
        Connection: close\r\n\r\n'''

        print '---- sending message'
        self.client.sendall(message)
        response = self.client.recv(1024)
        print '---- response received'
        print response
        print '---- following status code was present'
        statuscode = response[9:22]
        print statuscode

        print '---- end of test'
        self.assertEqual("404 NOT FOUND", statuscode)

    def test_HTTP200OKDIRWITHINDEX(self):
        print '---- testing HTTP 200 Ok response for request to a directory that contains index.html'

        message = '''GET /mp3/ HTTP/1.1\r\n
        Connection: close\r\n\r\n'''

        print '---- sending message'
        self.client.sendall(message)
        response = self.client.recv(1024)
        print '---- response received'
        print response
        print '---- following status code was present'
        statuscode = response[9:15]
        print statuscode

        print '---- end of test'
        self.assertEqual("200 OK", statuscode)

    def test_HTTP404DIRWITOUTHINDEX(self):
        print '---- testing HTTP 200 Ok response for request to a directory that contains index.html'

        message = '''GET /mp4/ HTTP/1.1\r\n
        Connection: close\r\n\r\n'''

        print '---- sending message'
        self.client.sendall(message)
        response = self.client.recv(1024)
        print '---- response received'
        print response
        print '---- following status code was present'
        statuscode = response[9:22]
        print statuscode

        print '---- end of test'
        self.assertEqual("404 NOT FOUND", statuscode)

    def test_MULTIPLEGETCONNCLOSED(self):
        print '----tesing multiple GETs, with last GET closing connection'

        message1 = '''GET /haiio_world.gif HTTP/1.1\r\n
        Connection: keep-alive\r\n\r\n'''

        message2 = '''GET /doesnotexit.png HTTP/1.1\r\n
        Connection: keep-alive\r\n\r\n'''

        message3 = '''GET /mp3/3pm.mp3 HTTP/1.1\r\n
        Connection: close\r\n\r\n'''
        print '---- sending messages'

        self.client.sendall(message1)
        time.sleep(1)
        print '---- receiving first answer:'
        response1 = self.client.recv(1024)
        print response1

        self.client.sendall(message2)
        time.sleep(1)
        print '---- receiving second answer:'
        response2 = self.client.recv(1024)
        print response2

        self.client.sendall(message3)
        time.sleep(1)
        print '---- receiving third answer:'
        response3 = self.client.recv(1024)
        print response3

        print '---- end of test'
        self.assertEqual(self.client.recv(1024), "")

    def test_MULTIPLEGETWAITCONNCLOSED(self):
        print '----testing multiple GETs, with last GET keeping connection alive, after timeout socket must be closed'

        message1 = '''GET /haiio_world.gif HTTP/1.1\r\n
        Connection: keep-alive\r\n\r\n'''

        message2 = '''GET /doesnotexit.png HTTP/1.1\r\n
        Connection: keep-alive\r\n\r\n'''

        message3 = '''GET /mp3/3pm.mp3 HTTP/1.1\r\n
        Connection: keep-alive\r\n\r\n'''

        print '---- sending messages'

        self.client.sendall(message1)
        time.sleep(1)
        print '---- receiving first answer:'
        response1 = self.client.recv(1024)
        print response1

        self.client.sendall(message2)
        time.sleep(1)
        print '---- receiving second answer:'
        response2 = self.client.recv(1024)
        print response2

        self.client.sendall(message3)
        time.sleep(1)
        print '---- receiving third answer:'
        response3 = self.client.recv(1024)
        print response3

        print '---- end of test'
        print '---- waiting for connection to die'
        time.sleep(10)
        print '---- connection should be dead now'

        self.assertEqual(self.client.recv(1024), "")

if __name__ == '__main__':
    unittest.main()