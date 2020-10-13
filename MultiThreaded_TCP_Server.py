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
            data = self.request.recv(1024)
            if not data:
                break

            #print("{} wrote:".format(self.client_address[0]))
            #print(data)
            printable = data.decode('ascii')
            print(' wrote ' + printable)

            cur_thread = threading.current_thread()

            #response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')

            response = createResponseMessage(data) 

            print('response: ' + response.decode('ascii') + cur_thread.name)

            #print('Sending back:')
            #print(response)

            self.request.sendall(response)


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
        sock.sendall(message)
        response = sock.recv(1024)
        print("Received: {}".format(response))


if __name__ == "__main__":
  
    serverParams = python_config.read_server_config()
    host = serverParams.get('host')
    port = int(serverParams.get('port'))
    print('Listening on HOST: ' + str(host) + ' and PORT: ' + str(port))

    #HOST, PORT = "localhost", 65432

    server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        client(ip, port, b"\x027|KEEPALIV\x03")
        #sleep(10)
        client(ip, port, b"\x028|KEEPALIV\x03")
        #sleep(10)
        client(ip, port, b"\x029|KEEPALIV\x03")

        #server.shutdown()
        server.serve_forever()
        