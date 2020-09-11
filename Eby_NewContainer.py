import ebybrownlibserver as libserver
import GlobalConstants
import Eby_Message

class NewContainer:

    #constructor
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.request[:].decode('ascii')
        self.fields = self.populateFields()
        self.MsgSequenceNumber = self.getMessageSequenceNumber()
        self.MessageID = self.fields[1]
        self.RouteNumber = self.fields[2]
        self.StopNumber = self.fields[3]
        self.ContainerID = self.fields[4]
        self.AssignmentID = self.fields[5]
        self.PickArea = self.fields[6]
        self.PickType = self.fields[7]
        self.Jurisdiction = self.fields[8]
        self.NumberCartons = self.getNumberCartons()  

    def populateFields(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields

    def getMessageSequenceNumber(self):
        msgSeqNumber =  self.fields[0][3:]
        return msgSeqNumber

    def getNumberCartons(self):
        numberCartons = self.fields[9].replace('0x3', '')
        return numberCartons
    
    
    

        


    