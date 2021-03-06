# echo_server.py

import socketserver
import Eby_Message
import python_config
import requests
import API_02_HostLog as hostLog
import Eby_Server2



class EbyTCPSocketHandler(socketserver.StreamRequestHandler):

    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        loggingConfig = python_config.read_logging_config()
        #enabled = loggingConfig.get('enabled')
        #api = loggingConfig.get('api')
        auth = loggingConfig.get('auth')
        domain = loggingConfig.get('domain')
        
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        #self.data = self.rfile.readline().strip()
        self.data = self.request.recv(1024)


        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        test = str(self.data, 'utf-8') #this works!!!
        #hostLog.log(auth, domain, "inbound", "ACK", test)

        response = self.createResponseMessage(self.data)
        print('Sending back:')
        print(response)

        #bytesToReturn = bytearray(response, 'ascii')

        #print('bytes to return:')
        #print(bytesToReturn)

        # Likewise, self.wfile is a file-like object used to write back
        # to the client
        self.wfile.write(response)
        #self.wfile.write(bytesToReturn)
    

    def createResponseMessage(self, message):
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
 

if __name__ == "__main__":

    serverParams = python_config.read_server_config()
    host = serverParams.get('host')
    port = int(serverParams.get('port'))
    print('Listening on HOST: ' + str(host) + ' and PORT: ' + str(port))
    
    HOST, PORT = host, port #"localhost", 9999

    # instantiate the server, and bind to localhost on port 9999
    #server = socketserver.TCPServer((HOST, PORT), EbyTCPSocketHandler)
    server = Eby_Server2.EchoServer((HOST, PORT), EbyTCPSocketHandler)

    # activate the server
    # this will keep running until Ctrl-C
    server.serve_forever()