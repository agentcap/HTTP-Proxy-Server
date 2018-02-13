import socket
import sys
import time

host = ""
port = 60005

if len(sys.argv) > 1:
    port = int(sys.argv[1])

server = socket.socket()

server.bind((host, port))
server.listen(5)
print "Proxy Server runing on port ", port

def parse_request(request):
    arr = request.split('\n')

    method  = arr[0].split(' ')[0]
    url     = arr[0].split(' ')[1]
    version = arr[0].split(' ')[2]

    # Removing http://
    if(url.find("http") != -1) :
        url = url[url.find("http")+7:]

    servername  = url.split('/')[0]
    path        = '/' + '/'.join(url.split('/')[1:])
    port        = 80

    if servername.find(":") != -1:
        idx         = servername.find(":");
        port        = int(servername[idx+1:])
        servername  = servername[:idx]

    arr[0]  = method + ' ' + path + ' ' + version + '\n'
    request = '\n'.join(arr)

    return [servername,port,request]


while True:
    conn, addr = server.accept()
    print 'Got connection from', addr

    req = conn.recv(1024)

    # Parse request
    host,port,req = parse_request(req);

    client = socket.socket()
    
    client.connect((host, port))
    print "Connection established with client"

    # temp = req.split('\n')

    # temp[0] = "GET / HTTP/1.1"
    # req = '\n'.join(temp)
    client.send(req)

    response = ''
    # time.sleep(1)
    while True:
        data = client.recv(1024)
        if not data:
            break
        response = response + data

    # time.sleep(1)
    print response


    conn.send(response)
    client.close()
 
    conn.close()
