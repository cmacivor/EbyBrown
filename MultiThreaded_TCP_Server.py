import socket
import threading
import socketserver
import Eby_Message
import python_config
import requests
import API_02_HostLog as hostLog
import time
import sys
import traceback
from time import sleep

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            data = str(self.request.recv(1024), 'ascii')
            if not data:
                break
            cur_thread = threading.current_thread()
            response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
            self.request.sendall(response)

        # data = str(self.request.recv(1024), 'ascii')
        # cur_thread = threading.current_thread()
        # response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
        # self.request.sendall(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def createResponseMessage(message):
        loggingConfig = python_config.read_logging_config()
        enabled = loggingConfig.get('enabled')
        api = loggingConfig.get('api')
        auth = loggingConfig.get('auth')
        domain = loggingConfig.get('domain')

        loggingNotEnabledMsg = "logging is not enabled in the config.ini."
        
        messageBase = Eby_Message.MessageBase(message)
        
        response = None  
            
        isKeepAliveMessage = messageBase.CheckIfMessageIsKeepAlive()
            
        if isKeepAliveMessage:
            response = messageBase.getFullAcknowledgeKeepAliveMessage()
            return response
        #if not, then it's a data message
        else:
            messageBase.getMessageType() #save the message data to the database, log it, etc.
            response = messageBase.getFullAcknowledgeKeepAliveMessage()
            if enabled == "1":
                hostLog.log(auth, domain, "WXS to Host", "ACKNOWLE", response)
            else:
                print(loggingNotEnabledMsg)
            return response


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        client(ip, port, "Hello World 1")
        sleep(10)
        client(ip, port, "Hello World 2")
        sleep(10)
        client(ip, port, "Hello World 3")

        server.shutdown()