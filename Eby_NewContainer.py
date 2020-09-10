import ebybrownlibserver as libserver
import GlobalConstants
import Eby_Message

class NewContainer:

    #constructor
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.request[:].decode('ascii')

    