import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    #s.sendall(b'\x027|KEEPALIV\x03')

    #s.sendall(b'\x02182|ADDCONTA|401   |330 |FC1005726-002  |FC1005726                |61    |Split Case|           |') # New Container
    s.sendall(b'\x0200013|ADDCONTA|307604|1123|SC307604112-006|307604112|006003|SPLITCASE|113205|20\x03') # New Container
    #s.sendall(b'\x0200013|CONTCOMP|SC307604112-006|307604112|1\x03') #Container Complete

    #s.sendall(b'\x02780|CONTCOMP|FH1005558-001  |FH1005558                |1|11  ') # a container complete from the actual system

    #s.sendall(b'\x0200013|ASGNCOMP|307604112\x03') #Assignment Complete
    #s.sendall(b'\x0200013|ORDRCOMP|307604|1123\x03') #Order Complete
    #s.sendall(b'\x0200013|ROUTCOMP|307604\x03') # Route Complete
    data = s.recv(1024)

print("Received", repr(data))