import socket
import Eby_Message
import Eby_MessageTCPServer
import python_config
import requests
import API_02_HostLog as hostLog
import time
import sys
import traceback
from queue import Queue
import atexit


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    loggingConfig = python_config.read_logging_config()
    auth = loggingConfig.get('auth')
    domain = loggingConfig.get('domain')
    api = loggingConfig.get("api")
    url = domain + api

    serverParams = python_config.read_server_config()
    host = serverParams.get('host')
    port = int(serverParams.get('port'))
    print('Listening on HOST: ' + str(host) + ' and PORT: ' + str(port))
    hostLog.log(auth, domain, "WXS Info", "Socket Listen", 'Listening on HOST: ' + str(host) + ' and PORT: ' + str(port))


    s.bind((host, port))
    s.listen()
    conn, addr = s.accept()
    data = b''
    with conn:
        print("Connected by", addr)
        hostLog.log(auth, domain, "WXS Info", "Socket Conn", "Connected from "+str(addr))
        while True:
            try:

                chunk = conn.recv(1024)
                #data = conn.recv(1024)

                # if not data:
                #     break
                data += chunk

                decodedData = data.decode('ascii')
                print(' wrote ' + decodedData)

                #messageBase = Eby_Message.MessageBase(data)
                messageBase = Eby_MessageTCPServer.MessageBaseTCPServer(decodedData)
            
                response = messageBase.getFullAcknowledgeKeepAliveMessage()
                #response = createResponseMessage(data)

                print('response: ' + response.decode('ascii'))
                conn.sendall(response)

                isKeepAliveMessage = messageBase.CheckIfMessageIsKeepAlive()
            
                if not isKeepAliveMessage:
                    hostLog.log(auth, domain, "Host to WXS", "UNKWN", data)
                
                data = b''

            except Exception as e:
                if isinstance(e, ConnectionResetError):
                    pass
                print(sys.exc_info()[0])
                print(traceback.format_exc())
                eMessage = "".join(e)
                hostLog.log(auth, domain, "WXS Info", "Socket Loss", "Exception | "+str(eMessage)+" | Restart TCP_SocketServer")
                print("press enter to continue...")
                input()



atexit.register(hostLog.log(auth, domain, "WXS Info", "Socket Info", "TCP_SocketServer Stopped in Task Scheduler"))
