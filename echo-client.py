import socket
from time import sleep

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    #s.sendall(b'\x027|KEEPALIV\x03')

    #.sendall(b'\x02384|ADDCONTA|401   |220 |FC1005755-002  |FC1005755                |61    |Split Case|                              |  ') # New Container
    #s.sendall(b'\x0200013|ADDCONTA|307604|1123|SC307604112-006|307604112|006003|SPLITCASE|113205|20\x03') # New Container
    #s.sendall(b'\x0200013|CONTCOMP|SC307604112-006|307604112|1\x03') #Container Complete
    #s.sendall(b'x0281|ADDCONTA|401   |220 |FC1005785-002  |FC1005785                |61    |Split Case|                              |  x03')

    #s.sendall(b'x02247|CONTCOMP|FZ2005798-001  |FZ2005798                |0|15x03') #Container Complete

    #s.sendall(b'\x02201|CONTCOMP|FZ2005783-001  |FZ2005783                |0|15') # a container complete from the actual system
    #s.sendall(b'x02199|CONTCOMP|FZ2005798-001  |FZ2005798                |1|15x03')

    #s.sendall(b'\x0200013|ASGNCOMP|307604112\x03') #Assignment Complete
    #s.sendall(b'x02248|ASGNCOMP|FZ2005798                x03') #Assignment Complete

    #s.sendall(b'\x0200013|ORDRCOMP|307604|1123\x03') #Order Complete
    #s.sendall(b'x02246|ORDRCOMP|401   |110 x03') #Order Complete

    #s.sendall(b'\x0200013|ROUTCOMP|307604\x03') # Route Complete
    #s.sendall(b'x02245|ROUTCOMP|401   x03') # Route Complete


    #s.sendall(b'x02248|ASGNCOMP|FZ2005798                x03') #Assignment Complete

    # sleep(1)

    #s.sendall(b'x02245|ROUTCOMP|401   x03') # Route Complete

    # sleep(1)

    #s.sendall(b'x02246|ORDRCOMP|401   |110 x03') #Order Complete

    # sleep(1)

    #s.sendall(b'x02199|CONTCOMP|FZ2005798-001  |FZ2005798                |1|15x03')

    # sleep(1)

    s.sendall(b'x0281|ADDCONTA|401   |220 |FC1005785-002  |FC1005785                |61    |Split Case|                              |  x03')


    data = s.recv(1024)

print("Received", repr(data))