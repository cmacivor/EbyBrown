import Eby_MessageProcessor as libserver
import Eby_GlobalConstants as GlobalConstants
import Eby_NewContainer
import Eby_ContainerComplete
import Eby_AssignmentComplete
import Eby_OrderComplete
import Eby_RouteComplete
import python_config
import requests
import API_02_HostLog as hostLog
import unicodedata
import string
import re

class MessageBaseTCPServer:
    KeepAliveRequestConstant = "KEEPALIV"
    KeepAliveResponseConstant = "ACKNOWLE"

    IsKeepAliveMessage = False
       
    #constructor
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.decode('ascii')  #libserver.request[:].decode('ascii')

    def CheckIfMessageIsKeepAlive(self):
        messageLength = len(self.AsciiRequestMessage) #len(self.libserver.request[:])
        doesContainKeepAlive = self.KeepAliveRequestConstant in self.AsciiRequestMessage #.decode('ascii') #self.libserver.request[:].decode('ascii')
        #if messageLength == 14 and doesContainKeepAlive: #Account for the extra characters created by hexadecimal values
        if doesContainKeepAlive:
            return True
        else:
            return False
    
    def getFullAcknowledgeKeepAliveMessage(self):
        fields = self.parsePipeDelimitedValues()
        #msgSeqNumber =  fields[0][1:] #remove the start transmission character
        #msgSeqNumber =  fields[0][1:]
        msgSeqNumber = str(fields[0])
       
        stringList = list(msgSeqNumber)
        msgLength = len(stringList)
        numberWithoutSTX = ""
        for index in range(1, msgLength):
            i = stringList[index]
            numberWithoutSTX += i

        fullMessage = GlobalConstants.StartTransmissionCharacter + numberWithoutSTX + "|" + self.KeepAliveResponseConstant + GlobalConstants.EndTransmissionCharacter
        return fullMessage.encode('ascii')

    def parsePipeDelimitedValues(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields
    
    # def logMessage(self, source, messageType, messageContent):
    #     loggingConfig = python_config.read_logging_config()
    #     enabled = loggingConfig.get('enabled')
    #     #api = loggingConfig.get('api')
    #     auth = loggingConfig.get('auth')
    #     domain = loggingConfig.get('domain')

    #     loggingNotEnabledMsg = "logging is not enabled in the config.ini."

    #     if enabled == "1":
    #         hostLog.log(auth, domain, source, messageType, messageContent)
    #     else:
    #         print(loggingNotEnabledMsg)


    # def getMessageType(self, connection):
  
    #     if GlobalConstants.NewContainer in self.AsciiRequestMessage:
    #         #self.logMessage("Host to WXS", GlobalConstants.NewContainer, self.AsciiRequestMessage)
    #         newContainer = Eby_NewContainer.NewContainer(self.libserver)
    #         result = newContainer.saveNewContainer()
    #         return GlobalConstants.NewContainer
    #     if GlobalConstants.ContainerComplete in self.AsciiRequestMessage:
    #         #self.logMessage("Host to WXS", GlobalConstants.ContainerComplete, self.AsciiRequestMessage)
    #         containerComplete = Eby_ContainerComplete.ContainerComplete(self.libserver)
    #         result = containerComplete.updateContainerAsComplete(connection)
    #         return GlobalConstants.ContainerComplete
    #     if GlobalConstants.AssignmentComplete in self.AsciiRequestMessage:
    #         #self.logMessage("Host to WXS", GlobalConstants.AssignmentComplete, self.AsciiRequestMessage)
    #         assignmentComplete = Eby_AssignmentComplete.AssignmentComplete(self.libserver)
    #         result = assignmentComplete.updateAssignmentComplete(connection)
    #         return GlobalConstants.AssignmentComplete
    #     if GlobalConstants.OrderComplete in self.AsciiRequestMessage:
    #         #self.logMessage("Host to WXS", GlobalConstants.OrderComplete, self.AsciiRequestMessage)
    #         orderComplete = Eby_OrderComplete.OrderComplete(self.libserver)
    #         result = orderComplete.updateOrderComplete(connection)
    #         return GlobalConstants.OrderComplete
    #     if GlobalConstants.RouteComplete in self.AsciiRequestMessage:
    #         #self.logMessage("Host to WXS", GlobalConstants.RouteComplete, self.AsciiRequestMessage)
    #         routeComplete = Eby_RouteComplete.RouteComplete(self.libserver)
    #         result = routeComplete.updateRouteComplete(connection)
    #         return GlobalConstants.RouteComplete
            
      
            


    