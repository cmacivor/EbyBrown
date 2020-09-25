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

class MessageBase:
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
        if messageLength == 14 and doesContainKeepAlive: #Account for the extra characters created by hexadecimal values
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

        #TODO determine if what's coming over will be ASCII or binary. See this: https://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3
        # fullMessage = GlobalConstants.StartTransmissionCharacter + msgSeqNumber + self.KeepAliveResponseConstant + GlobalConstants.EndTransmissionCharacter
        fullMessage = GlobalConstants.StartTransmissionCharacter + numberWithoutSTX + "|" + self.KeepAliveResponseConstant + GlobalConstants.EndTransmissionCharacter
        return fullMessage.encode('ascii')

    def parsePipeDelimitedValues(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields
    
    def logMessage(self, source, messageType, messageContent):
        loggingConfig = python_config.read_logging_config()
        enabled = loggingConfig.get('enabled')
        #api = loggingConfig.get('api')
        auth = loggingConfig.get('auth')
        domain = loggingConfig.get('domain')

        loggingNotEnabledMsg = "logging is not enabled in the config.ini."

        if enabled == "1":
            hostLog.log(auth, domain, source, messageType, messageContent)
            #hostLog.log(auth, domain, "WXS to Lucas", "ACKNOWLE", responseMessage)
        else:
            print(loggingNotEnabledMsg)


    def getMessageType(self):
  
        if GlobalConstants.NewContainer in self.AsciiRequestMessage:
            newContainer = Eby_NewContainer.NewContainer(self.libserver)
            self.logMessage("Lucas to WXS", GlobalConstants.NewContainer, self.AsciiRequestMessage)
            result = newContainer.saveNewContainer()
            return result
        if GlobalConstants.ContainerComplete in self.AsciiRequestMessage:
            containerComplete = Eby_ContainerComplete.ContainerComplete(self.libserver)
            self.logMessage("Lucas to WXS", GlobalConstants.ContainerComplete, self.AsciiRequestMessage)
            result = containerComplete.updateContainerAsComplete()
            return result
        if GlobalConstants.AssignmentComplete in self.AsciiRequestMessage:
            assignmentComplete = Eby_AssignmentComplete.AssignmentComplete(self.libserver)
            self.logMessage("Lucas to WXS", GlobalConstants.AssignmentComplete, self.AsciiRequestMessage)
            result = assignmentComplete.updateAssignmentComplete()
            return result
        if GlobalConstants.OrderComplete in self.AsciiRequestMessage:
            orderComplete = Eby_OrderComplete.OrderComplete(self.libserver)
            self.logMessage("Lucas to WXS", GlobalConstants.OrderComplete, self.AsciiRequestMessage)
            result = orderComplete.updateOrderComplete()
            return result
        if GlobalConstants.RouteComplete in self.AsciiRequestMessage:
            routeComplete = Eby_RouteComplete.RouteComplete(self.libserver)
            self.logMessage("Lucas to WXS", GlobalConstants.RouteComplete, self.AsciiRequestMessage)
            result = routeComplete.updateRouteComplete()
            return result
            
      
            


    