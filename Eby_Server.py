# echo_server.py

import socketserver
import Eby_Message

class EbyTCPSocketHandler(socketserver.StreamRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
          

        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        self.data = self.rfile.readline().strip()

        response = self.createResponseMessage(self.data)

        print("{} wrote:".format(self.client_address[0]))
        print(self.data)

        # Likewise, self.wfile is a file-like object used to write back
        # to the client
        self.wfile.write(response)
    

    def createResponseMessage(self, message):

        messageBase = Eby_Message.MessageBase(message)
        
        response = None  
            
        isKeepAliveMessage = messageBase.CheckIfMessageIsKeepAlive()
            
        if isKeepAliveMessage:
            response = messageBase.getFullAcknowledgeKeepAliveMessage()
            return response
        #if not, then it's a data message
        else:
            #messageBase.getMessageType() #save the message data to the database, log it, etc.
            response = messageBase.getFullAcknowledgeKeepAliveMessage()
            return response
 

if __name__ == "__main__":
    
    HOST, PORT = "localhost", 9999

    # instantiate the server, and bind to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), EbyTCPSocketHandler)

    # activate the server
    # this will keep running until Ctrl-C
    server.serve_forever()