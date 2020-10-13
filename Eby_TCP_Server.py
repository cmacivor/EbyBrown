import socket
import Eby_Message
import python_config
import requests
import API_02_HostLog as hostLog
import time
import sys
import traceback
from queue import Queue

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
               
            # if enabled == "1":
            #     #log inbound message               
            #     hostLog.log(auth, domain, "Host to WXS", "KEEPALIV", message)
            #     #log the response from WXS
            #     hostLog.log(auth, domain, "WXS to Host", "ACKNOWL", response)
            # else:
            #     print(loggingNotEnabledMsg)
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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

   # messagesQueue = Queue(0)
    
    loggingConfig = python_config.read_logging_config()
    auth = loggingConfig.get('auth')
    domain = loggingConfig.get('domain')
    api = loggingConfig.get("api")
    url = domain + api

    serverParams = python_config.read_server_config()
    host = serverParams.get('host')
    port = int(serverParams.get('port'))
    print('Listening on HOST: ' + str(host) + ' and PORT: ' + str(port))


    s.bind((host, port))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("Connected by", addr)
        while True:
            try:

                data = conn.recv(1024)

                if not data:
                    break

                printable = data.decode('ascii')
                print(' wrote ' + printable)

                #messagesQueue.put(data)

                #messageBase = Eby_Message.MessageBase(data)

                #response = messageBase.getFullAcknowledgeKeepAliveMessage()
                response = createResponseMessage(data)

                print('response: ' + response.decode('ascii'))
                conn.sendall(response)
            except Exception as e:
                if isinstance(e, ConnectionResetError):
                    pass
                print(sys.exc_info()[0])
                print(traceback.format_exc())
                print("press enter to continue...")
                input()

        # sentinel = object()
        # while True:
        #     currentQueueSize = messagesQueue.qsize()
        #     if currentQueueSize > 0:
        #         for message in iter(messagesQueue.get, sentinel):
        #             print('current size')
        #             createResponseMessage(message)


        


 