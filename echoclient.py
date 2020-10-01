import socket
from time import sleep

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    s.sendall(b'Hello, world')
    data = s.recv(1024)
    print(data)
    
    sleep(10)

    s.sendall(b'Hello, world 2')
    data1 = s.recv(1024)
    print(data1)

    sleep(10)

    s.sendall(b'Hello, world 3')
    data2 = s.recv(1024)
    print(data2)


#print('Received', repr(data))