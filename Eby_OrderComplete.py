import Eby_MessageProcessor as libserver
import GlobalConstants
import Eby_Message
import re # regular expressions


class OrderComplete:
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.request[:].decode('ascii')
        self.fields = self.populateFields()
        self.MsgSequenceNumber = self.getMessageSequenceNumber()
        self.MessageID = self.fields[1]
        self.Route = self.fields[2]
        self.Stop = self.getStop()
        

    def populateFields(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields

    def getMessageSequenceNumber(self):
        msgSeqNumber =  self.fields[0][3:]
        return msgSeqNumber
    
    def getStop(self):
        stop = self.fields[3].replace('0x3', '')
        return stop