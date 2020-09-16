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
            print("{} wrote:".format(self.client_address[0]))
            print(self.data)
            # Likewise, self.wfile is a file-like object used to write back
            # to the client
            self.wfile.write(self.data.upper())
    # def handle(self):
    #     # self.request is the TCP socket connected to the client
    #     self.data = self.request.recv(1024).strip()
    #     print("{} wrote:".format(self.client_address[0]))
    #     print(self.data)
    #     # just send back the same data, but upper-cased
    #     self.request.sendall(self.data.upper())

if __name__ == "__main__":
    
    HOST, PORT = "localhost", 9999

    # instantiate the server, and bind to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), EbyTCPSocketHandler)

    # activate the server
    # this will keep running until Ctrl-C
    server.serve_forever()