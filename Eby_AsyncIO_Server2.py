from twisted.internet import protocol, reactor, endpoints
import Eby_Message
import python_config
import requests
import API_02_HostLog as hostLog
import time
import sys
import traceback
from time import sleep


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


class Echo(protocol.Protocol):
    def dataReceived(self, data):

        response = createResponseMessage(data)

        #self.transport.write(data)
        self.transport.write(response)

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

endpoints.serverFromString(reactor, "tcp:65432:interface=127.0.0.1").listen(EchoFactory())
reactor.run()