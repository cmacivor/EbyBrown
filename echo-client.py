import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 9999  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    #s.sendall(b'\x027|KEEPALIV\x03')
    s.sendall(b'\x0200013|ADDCONTA|307604|1123|SC307604112-006|307604112|006003|SPLITCASE|113205|20\x03')
    data = s.recv(1024)

print("Received", repr(data))