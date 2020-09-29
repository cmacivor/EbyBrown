import socket
import Eby_Message
import python_config
import requests
import API_02_HostLog as hostLog


def createResponseMessage(message):
        loggingConfig = python_config.read_logging_config()
        enabled = loggingConfig.get('enabled')
        #api = loggingConfig.get('api')
        auth = loggingConfig.get('auth')
        domain = loggingConfig.get('domain')

        loggingNotEnabledMsg = "logging is not enabled in the config.ini."
        
        messageBase = Eby_Message.MessageBase(message)
        
        response = None  
            
        isKeepAliveMessage = messageBase.CheckIfMessageIsKeepAlive()
            
        if isKeepAliveMessage:
            response = messageBase.getFullAcknowledgeKeepAliveMessage()
                #log inbound message
            if enabled == "1":
                decodedMessage = str(message.decode('utf-8'))
                hostLog.log(auth, domain, "Lucas to WXS", "KEEPALIV", decodedMessage)
                #hostLog.log(auth, domain, "WXS to Lucas", "ACKNOWLE", response.decode('utf-8'))
            else:
                print(loggingNotEnabledMsg)
            return response
        #if not, then it's a data message
        else:
            messageBase.getMessageType() #save the message data to the database, log it, etc.
            response = messageBase.getFullAcknowledgeKeepAliveMessage()
            if enabled == "1":
                hostLog.log(auth, domain, "WXS to Lucas", "ACKNOWLE", response)
            else:
                print(loggingNotEnabledMsg)
            return response

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    loggingConfig = python_config.read_logging_config()
    auth = loggingConfig.get('auth')
    domain = loggingConfig.get('domain')

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
            data = conn.recv(1024)
            if not data:
                break
            printable = data.decode('ascii')
            print(' wrote ' + printable)
            response = createResponseMessage(data)
            print('response: ' + response.decode('ascii'))
            conn.sendall(response)
            # try:
            #     data = conn.recv(1024)
            #     if not data:
            #         break
            #     printable = data.decode('ascii')
            #     print(addr + ' wrote ' + printable)
            #     response = createResponseMessage(data)
            #     print('response: ' + response.decode('ascii'))
            #     conn.sendall(response)
            # except:
            #     pass
            # else:
            #     break


 