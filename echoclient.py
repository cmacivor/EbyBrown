import socket
from time import sleep

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        s.sendall(b'\x027|KEEPALIV\x03')
        data = s.recv(1024)
        print(data)
        sleep(3)

  
    
    # #sleep(10)

    # s.sendall(b'\x027|KEEPALIV\x03')
    # data1 = s.recv(1024)
    # print(data1)

    # #sleep(10)

    # s.sendall(b'\x027|KEEPALIV\x03')
    # data2 = s.recv(1024)
    # print(data2)


#print('Received', repr(data))