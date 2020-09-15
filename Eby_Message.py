import Eby_MessageProcessor as libserver
import Eby_GlobalConstants as GlobalConstants
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
    
    def getFullAcknowledgeKeepAliveMessage(self):
        fields = self.parsePipeDelimitedValues()
        msgSeqNumber =  fields[0][3:] #remove the start transmission character
    
        #TODO determine if what's coming over will be ASCII or binary. See this: https://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3
        # fullMessage = GlobalConstants.StartTransmissionCharacter + msgSeqNumber + self.KeepAliveResponseConstant + GlobalConstants.EndTransmissionCharacter
        fullMessage = GlobalConstants.StartTransmissionCharacter + msgSeqNumber + "|" + self.KeepAliveResponseConstant + GlobalConstants.EndTransmissionCharacter
        return fullMessage.encode('ascii')

    def parsePipeDelimitedValues(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields


    def getMessageType(self):

        if GlobalConstants.NewContainer in self.AsciiRequestMessage:
            newContainer = Eby_NewContainer.NewContainer(self.libserver)
            result = newContainer.saveNewContainer()
            return result
        if GlobalConstants.ContainerComplete in self.AsciiRequestMessage:
            containerComplete = Eby_ContainerComplete.ContainerComplete(self.libserver)
            result = containerComplete.updateContainerAsComplete()
            return result
        if GlobalConstants.AssignmentComplete in self.AsciiRequestMessage:
            assignmentComplete = Eby_AssignmentComplete.AssignmentComplete(self.libserver)
            result = assignmentComplete.updateAssignmentComplete()
            return result
        if GlobalConstants.OrderComplete in self.AsciiRequestMessage:
            orderComplete = Eby_OrderComplete.OrderComplete(self.libserver)
            return orderComplete
        if GlobalConstants.RouteComplete in self.AsciiRequestMessage:
            routeComplete = Eby_RouteComplete.RouteComplete(self.libserver)
            return routeComplete
            
      
            


    