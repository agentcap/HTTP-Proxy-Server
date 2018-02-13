import socket
import sys
import time

host = ""
port = 60005
# if len(sys.argv) > 2:
#     port = sys.argv[2]

server = socket.socket()
print "Socket created"

server.bind((host, port))
server.listen(5)

while True:
    conn, addr = server.accept()
    print 'Got connection from', addr

    req = conn.recv(1024)
    print "Client Req",req

    # Parse request

    client = socket.socket()
    
    host = "localhost"
    port = 20000

    client.connect((host, port))
    print "Connection established with client"

    # temp = req.split('\n')

    # temp[0] = "GET / HTTP/1.1"
    # req = '\n'.join(temp)
    client.send(req)

    time.sleep(1)
    response = client.recv(1024)
    time.sleep(1)
    print response


    conn.send(response)
    client.close()
 
    conn.close()
