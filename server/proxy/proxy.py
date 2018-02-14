import socket
import sys
import time
import datetime

# host,port,path,last_Accessed,time
cache = []

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

    arr[0]  = method + ' ' + path + ' ' + version
    request = '\n'.join(arr)

    return [servername,port,path,request]

def is_cached(host,port,path,req,conn):

    print "Enterd is_cached function"
    # Whether requeste matches obj present in cache
    cache_idx = -1
    for i in range(len(cache)):
        obj = cache[i]
        if(obj["host"] == host and obj["port"] == port and obj["path"] == path):
            cache_idx = i
            break

    if(cache_idx == -1):
        print "Not present in cache"
        return False


    # If in cache conditional get
    time_header = "If-Modified-Since: %s" % (cache[cache_idx]["last_mod"])
    cond_req = req.split('\n')
    cond_req.insert(1,time_header)
    cond_req = '\n'.join(cond_req)

    # Sending Conditional get request
    server_socket = socket.socket()
    server_socket.connect((host, port))
    server_socket.send(cond_req)

    time.sleep(1)
    data = server_socket.recv(1024)
    time.sleep(1)

    print "$$$$$$$$$$$$$$$$$$$$$$$$$"
    print "$$$$$$$$$$$$$$$$$$$$$$$$$"
    print "$$$$$$$$$$$$$$$$$$$$$$$$$"
    print "$$$$$$$$$$$$$$$$$$$$$$$$$"
    print data
    print "$$$$$$$$$$$$$$$$$$$$$$$$$"
    print "$$$$$$$$$$$$$$$$$$$$$$$$$"
    print "$$$$$$$$$$$$$$$$$$$$$$$$$"
    print "$$$$$$$$$$$$$$$$$$$$$$$$$"

    # If file is not modified send the cached values and update queue order
    if(data.split(' ')[1] == "304" ):
        print "Cache up to date"
        while True:
            if(data):
                break
            data = server_socket.recv(1024)
        send_cache(cache_idx,conn)

    # Filter the above content and store in cache
    elif(data.split(' ')[1] == "200"):
        print "Modified cache page"
        obj = {}
        obj["host"] = host
        obj["port"] = port
        obj["path"] = path
        obj["time"] = time.time()
        obj["last_mod"] = find_date(data)

        idx = cache_position()
        cache[idx] = obj
        with open(str(idx), 'wb') as file:
            while True:
                if(not data):
                    file.close()
                    break
                file.write(data)
                
                data = server_socket.recv(1024)
        file.close()
        send_cache(idx,conn)

    # Handling other response messages like 404,....
    else:
        while True:
            if(data):
                break
            conn.send(data)
            data = server_socket.recv(1024)

    server_socket.close()
    return True

def find_date(data):
    idx = data.find("Last-Modified:")
    # if(idx != -1) Handle this later

    date = data[idx+len("Last-Modified: "):].split("\n")[0]

    print "!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print "Date is ", date
    print "idx is ", idx
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print "!!!!!!!!!!!!!!!!!!!!!!!!!!"
    # new_date = time.strptime(date,"%a, %d %b %Y %H:%M:%S %Z")
    # print new_date
    # date = date.strip
    # dt = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %Z')
    # return dt.strftime('%a %b %d %H:%M:%S') + ' GMT ' + dt.strftime('%Y')
    return "Tue Feb 13 18:53:59 GMT 2018"


def cache_position():
    if(len(cache) < 3):
        cache.append({})
        return len(cache)-1

    min_time = cache[0]["time"]
    idx = 0
    for i in range(len(cache)):
        if(min_time > cache[i]["time"]):
            idx = i

    return idx


def send_cache(idx,conn):
    file = open(str(idx),'r')
    cache[idx]["time"] = time.time()
    data = file.read(1024)
    while True:
        if(not data):
            file.close()
            break
        conn.send(data)
        data = file.read(1024)


def handle_client(conn):
    """
        This function takes the connection which was accepted by the server
        and acts as proxy for the client request

        "conn" is the socket connection to the client
    """
    req = conn.recv(1024)

    # Parse request
    host,port,path,req = parse_request(req);

    # Handle caching
    if(is_cached(host,port,path,req,conn)):
        return

    # If not in cache contacting the server and passsing
    # the request of the client
    server_socket = socket.socket()
    server_socket.connect((host, port))
    print "Connection established with main server"
    server_socket.send(req)


    # Read the response from the server untill all the 
    # headers are reached
    time.sleep(1)
    data = server_socket.recv(1024)
    time.sleep(1)

    obj = {}
    obj["host"] = host
    obj["port"] = port
    obj["path"] = path
    obj["time"] = time.time()
    obj["last_mod"] = find_date(data)

    idx = cache_position()
    cache[idx] = obj
    with open(str(idx), 'wb') as file:
        while True:
            if(not data):
                file.close()
                break
            file.write(data)
            
            data = server_socket.recv(1024)
    file.close()
    send_cache(idx,conn)

    server_socket.close()
    conn.close()

def server(host,port):
    """
        Run's the proxy server on the given host and port
    """
    server = socket.socket()

    server.bind((host, port))
    server.listen(5)
    print "Proxy Server runing on port ", port

    while True:
        conn, addr = server.accept()
        print 'Got connection from', addr

        handle_client(conn)

host = ""
port = 60005

if len(sys.argv) > 1:
    port = int(sys.argv[1])

server(host,port)