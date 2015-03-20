# HTTP-Server
Get Request HTTP Server

This is a simple HTTP Server written in python.
It sets up a server that binds to localhost on a port (default 8090).
Clients that connect to the socket can send HTTP GET Requests (HTTP 1.1).
The server will parse and send corresponding responses.
The folder "Content" contains the files that are available to the server.

***How to run it?***
Run server.py
Disable any firewall (these will block connections to the server)
Open up a browser and type some of the following lines in the address bar:
- http://localhost:8090/wiki_hash_page.html
- http://localhost:8090/hello_world.gif

"8090" is the port the server is listening on (can be changed in server.py)
"localhost" is the address of the server
Other files can be added to the folder "Content" manually and can also be requested.

***Usefull links***

http://pymotw.com/2/socket/tcp.html
https://docs.python.org/3/howto/sockets.html
https://docs.python.org/2/library/threading.html
http://www.pythoncentral.io/how-to-create-a-thread-in-python/
http://www.lagmonster.org/docs/vi.html
http://stackoverflow.com/questions/4642345/python-client-server-question
http://stackoverflow.com/questions/4685217/parse-raw-http-headers
http://pymotw.com/2/BaseHTTPServer/
http://nullege.com/codes/search/BaseHTTPServer.BaseHTTPRequestHandler.parse_request

***To Do:***
	- create a test suite using the unittest framework: https://docs.python.org/2/library/unittest.html.
	- implement all the test scenario's that are specified in the project