import GlobalConstants

#A generic class representing the various Data Message types
class DataMessage:

     #constructor
    def __init__(self, libserver):
        self.libserver = libserver
    
    

    #this is for a Data Message
    def getMessageIdentifier(self):
        messageID = self.libserver.request[6:14]
        return messageID

    def getMessageType(self):
        messageID = self.getMessageIdentifier()
        if messageID == GlobalConstants.NewContainer:  
            #TODO: instantiate NewContainer class
        if messageID == GlobalConstants.ContainerComplete:
            #TODO: instantiate ContainerComplete class

    