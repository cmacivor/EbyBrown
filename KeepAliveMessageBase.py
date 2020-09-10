import ebybrownlibserver as libserver
import GlobalConstants

class KeepAlive:
    KeepAliveRequestConstant = "KEEPALIV"
    KeepAliveResponseConstant = "ACKNOWLE"
   
    #constructor
    def __init__(self, libserver):
        self.libserver = libserver

    def getMessageSequenceNumber(self):
        msgSeqNumber = self.libserver.request[3:8] #starting at position 3 because the hex "2" reads as "0x2".
        return msgSeqNumber
    
    def getFullAcknowledgeMessage(self):
        msgSeqNumber = self.getMessageSequenceNumber()
        #TODO determine if what's coming over will be ASCII or binary. See this: https://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3
        # fullMessage = GlobalConstants.StartTransmissionCharacter + msgSeqNumber + self.KeepAliveResponseConstant + GlobalConstants.EndTransmissionCharacter
        decodedMsgSeqNumber = msgSeqNumber.decode('ascii')
        fullMessage = GlobalConstants.StartTransmissionCharacter + decodedMsgSeqNumber + self.KeepAliveResponseConstant + GlobalConstants.EndTransmissionCharacter
        return fullMessage.encode('ascii')

    