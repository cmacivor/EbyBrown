import logging
import sys
import socketserver
import datetime

class EchoRequestHandler(socketserver.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('EchoRequestHandler')
        self.logger.debug('__init__')
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        self.logger.debug('setup')
        return socketserver.BaseRequestHandler.setup(self)

    def handle(self):
        self.logger.debug('handle')

        # Echo the back to the client
        data = self.request.recv(1024)
        self.logger.debug('recv()->"%s"', data)
        self.request.send(data)
        return

    def finish(self):
        self.logger.debug('finish')
        return socketserver.BaseRequestHandler.finish(self)


class EchoServer(socketserver.TCPServer):
    
    def __init__(self, server_address, handler_class=EchoRequestHandler):
        self.logger = logging.getLogger('EchoServer')
        self.logger.debug('__init__')
        print('__init__')
        socketserver.TCPServer.__init__(self, server_address, handler_class)
        return

    def server_activate(self):
        self.logger.debug('server_activate')
        print('server_activate')
        socketserver.TCPServer.server_activate(self)
        return

    def serve_forever(self):
        self.logger.debug('waiting for request')
        print('waiting for request')
        self.logger.info('Handling requests, press <Ctrl-C> to quit')
        print('Handling requests, press <Ctrl-C> to quit')
        while True:
            self.handle_request()
        return

    def handle_request(self):
        now = datetime.datetime.now()
        #self.logger.debug('handle_request')
        #print('handle_request time: ' + now.strftime("%Y-%m-%d %H:%M:%S"))
        return socketserver.TCPServer.handle_request(self)

    def verify_request(self, request, client_address):
        now = datetime.datetime.now()
        self.logger.debug('verify_request(%s, %s)', request, client_address)
        print('verify_request time: ' + now.strftime("%Y-%m-%d %H:%M:%S"))
        return socketserver.TCPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        now = datetime.datetime.now()
        self.logger.debug('process_request(%s, %s)', request, client_address)
        print('process_request time: ' + now.strftime("%Y-%m-%d %H:%M:%S"))
        return socketserver.TCPServer.process_request(self, request, client_address)

    def server_close(self):
        now = datetime.datetime.now()
        self.logger.debug('server_close time: ' + now.strftime("%Y-%m-%d %H:%M:%S"))
        print('server_close time ' + now.strftime("%Y-%m-%d %H:%M:%S"))
        return socketserver.TCPServer.server_close(self)

    def finish_request(self, request, client_address):
        now = datetime.datetime.now()
        self.logger.debug('finish_request(%s, %s)', request, client_address)
        print('finish_request time ' + now.strftime("%Y-%m-%d %H:%M:%S"))
        return socketserver.TCPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        now = datetime.datetime.now()
        self.logger.debug('close_request(%s)', request_address)
        print('close_request ' + now.strftime("%Y-%m-%d %H:%M:%S"))
        return socketserver.TCPServer.close_request(self, request_address)

    
    