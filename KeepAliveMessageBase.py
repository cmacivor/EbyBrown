import ebybrownlibserver as libserver

class KeepAlive:
    def __init__(self, libserver):
        self.libserver = libserver

    def getMessageSequenceNumber(self):
        msgSeqNumber = self.libserver.request[3:9]
        return msgSeqNumber