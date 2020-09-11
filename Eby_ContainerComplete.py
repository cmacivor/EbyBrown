import ebybrownlibserver as libserver
import GlobalConstants
import Eby_Message

class ContainerComplete:
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.request[:].decode('ascii')
        self.fields = self.populateFields()
        self.MsgSequenceNumber = self.getMessageSequenceNumber()
        self.MessageID = self.fields[1]
        self.ContainerID = self.fields[2]
        self.AssignmentID = self.fields[3]
        self.QCFlag = self.getQCFlag()  #self.fields[4][:1]


    def populateFields(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields

    def getMessageSequenceNumber(self):
        msgSeqNumber =  self.fields[0][3:]
        return msgSeqNumber
    
    def getQCFlag(self):
        qcflag = self.fields[4].replace('0x3', '')
        return qcflag