import asyncio
import Eby_Message
import python_config
import API_02_HostLog as hostLog
import sys
import traceback


async def handle_echo(reader, writer):
    
    while True:
        try:
            data = await reader.read(1024)

            if not data:
                break

            printable = data.decode('ascii')
            print(' wrote ' + printable)

            messageBase = Eby_Message.MessageBase(data)

            response = messageBase.getFullAcknowledgeKeepAliveMessage()

            print('response: ' + response.decode('ascii'))

            writer.write(response)
            await writer.drain()
            responseMessage = createResponseMessage(data)
        except Exception:
            print(sys.exc_info()[0])
            print(traceback.format_exc())
            print("press enter to continue...")
            input()
        

    #print("Close the connection")
    #writer.close()

async def main():
    serverParams = python_config.read_server_config()
    host = serverParams.get('host')
    port = int(serverParams.get('port'))

    server = await asyncio.start_server(
        handle_echo, host, port)


    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

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
        # if enabled == "1":
        #     decodedMessage = str(message.decode('utf-8'))
        #     hostLog.log(auth, domain, "Lucas to WXS", "KEEPALIV", decodedMessage)
        #     #hostLog.log(auth, domain, "WXS to Lucas", "ACKNOWLE", response.decode('utf-8'))
        # else:
        #     print(loggingNotEnabledMsg)
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

asyncio.run(main())