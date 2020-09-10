import ebybrownlibserver as libserver

class KeepAlive:
    def __init__(self, libserver):
        self.libserver = libserver

    # def getMessageSequenceNumber:
    #     msgSeqNumber = self.libserver[3:9]
    #     return msgSeqNumber