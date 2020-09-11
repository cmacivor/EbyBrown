import ebybrownlibserver as libserver
import GlobalConstants
import Eby_NewContainer
import Eby_ContainerComplete
import Eby_AssignmentComplete
import Eby_OrderComplete
import Eby_RouteComplete

class MessageBase:
    KeepAliveRequestConstant = "KEEPALIV"
    KeepAliveResponseConstant = "ACKNOWLE"

    IsKeepAliveMessage = False
       
    #constructor
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.request[:].decode('ascii')

    def CheckIfMessageIsKeepAlive(self):
        messageLength = len(self.libserver.request[:])
        doesContainKeepAlive = self.KeepAliveRequestConstant in self.libserver.request[:].decode('ascii')
        if messageLength == 20 and doesContainKeepAlive: #Account for the extra characters created by hexadecimal values
            return True
        else:
            return False

    # def getMessageSequenceNumber(self):
    #     msgSeqNumber = self.libserver.request[3:8] #starting at position 3 because the hex "2" reads as "0x2".
    #     return msgSeqNumber
    
    def getFullAcknowledgeKeepAliveMessage(self):
        fields = self.parsePipeDelimitedValues()
        msgSeqNumber =  fields[0][3:] #remove the start transmission character
    
        #TODO determine if what's coming over will be ASCII or binary. See this: https://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3
        # fullMessage = GlobalConstants.StartTransmissionCharacter + msgSeqNumber + self.KeepAliveResponseConstant + GlobalConstants.EndTransmissionCharacter
        fullMessage = GlobalConstants.StartTransmissionCharacter + msgSeqNumber + self.KeepAliveResponseConstant + GlobalConstants.EndTransmissionCharacter
        return fullMessage.encode('ascii')

    def parsePipeDelimitedValues(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields


     #this is for a Data Message
     #TODO doing things this way may not work if the length can vary 
    # def getMessageIdentifier(self):
    #     messageID = self.libserver.request[6:14]
    #     return messageID

    def getMessageType(self):

        if GlobalConstants.NewContainer in self.AsciiRequestMessage:
            newContainer = Eby_NewContainer.NewContainer(self.libserver)
            return newContainer
        if GlobalConstants.ContainerComplete in self.AsciiRequestMessage:
            containerComplete = Eby_ContainerComplete.ContainerComplete(self.libserver)
            return containerComplete
        if GlobalConstants.AssignmentComplete in self.AsciiRequestMessage:
            assignmentComplete = Eby_AssignmentComplete.AssignmentComplete(self.libserver)
            return assignmentComplete
        if GlobalConstants.OrderComplete in self.AsciiRequestMessage:
            orderComplete = Eby_OrderComplete.OrderComplete(self.libserver)
            return orderComplete
        if GlobalConstants.RouteComplete in self.AsciiRequestMessage:
            routeComplete = Eby_RouteComplete.RouteComplete(self.libserver)
            return routeComplete
            
      
            


    