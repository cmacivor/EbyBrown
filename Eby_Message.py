import Eby_MessageProcessor as libserver
import Eby_GlobalConstants as GlobalConstants
import Eby_NewContainer
import Eby_ContainerComplete
import Eby_AssignmentComplete
import Eby_OrderComplete
import Eby_RouteComplete
import python_config
import requests
import API_02_HostLog as log
import unicodedata
import string
import re
import mysql.connector

class MessageBase:
    KeepAliveRequestConstant = "KEEPALIV"
    KeepAliveResponseConstant = "ACKNOWLE"

    IsKeepAliveMessage = False
       
    #constructor
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.replace("'", "")   #libserver.decode('ascii')  #libserver.request[:].decode('ascii')

    def CheckIfMessageIsKeepAlive(self):
        messageLength = len(self.AsciiRequestMessage) #len(self.libserver.request[:])
        doesContainKeepAlive = self.KeepAliveRequestConstant in self.AsciiRequestMessage #.decode('ascii') #self.libserver.request[:].decode('ascii')
        #if messageLength == 14 and doesContainKeepAlive: #Account for the extra characters created by hexadecimal values
        if doesContainKeepAlive:
            return True
        else:
            return False
    
    def getFullAcknowledgeKeepAliveMessage(self):
        fields = self.parsePipeDelimitedValues()
        #msgSeqNumber =  fields[0][1:] #remove the start transmission character
        #msgSeqNumber =  fields[0][1:]
        msgSeqNumber = str(fields[0])
       
        stringList = list(msgSeqNumber)
        msgLength = len(stringList)
        numberWithoutSTX = ""
        for index in range(1, msgLength):
            i = stringList[index]
            numberWithoutSTX += i

        fullMessage = GlobalConstants.StartTransmissionCharacter + numberWithoutSTX + "|" + self.KeepAliveResponseConstant + GlobalConstants.EndTransmissionCharacter
        return fullMessage.encode('ascii')

    def parsePipeDelimitedValues(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields
    
    # def logMessage(self, source, messageType, messageContent):
    #     loggingConfig = python_config.read_logging_config()
    #     enabled = loggingConfig.get('enabled')
    #     #api = loggingConfig.get('api')
    #     auth = loggingConfig.get('auth')
    #     domain = loggingConfig.get('domain')

    #     loggingNotEnabledMsg = "logging is not enabled in the config.ini."

    #     if enabled == "1":
    #         hostLog.log(auth, domain, source, messageType, messageContent)
    #     else:
    #         print(loggingNotEnabledMsg)

    def update_host_log_as_processed(self, hostLogId, messageType):
        config = python_config.read_db_config()

        host = config.get('host')
        user = config.get('user')
        wcsDatabase = config.get('wcsdatabase')
        password = config.get('password')

        try:
            connection = mysql.connector.connect(
                host= host, 
                user= user, 
                database= wcsDatabase, 
                password= password 
            )

            cursor = connection.cursor()
    
            sql = "UPDATE host_logs SET type = %s where id = %s"

            updateValues = (messageType, hostLogId)

            cursor.execute(sql, updateValues)

            connection.commit()

            cursor.close()
            connection.close()

        except Exception as e:
            print(e)
        finally:
            cursor.close()
            connection.close()
    
    def update_host_log_as_no_update(self, hostLogId):
        config = python_config.read_db_config()

        host = config.get('host')
        user = config.get('user')
        wcsDatabase = config.get('wcsdatabase')
        password = config.get('password')

        try:
            connection = mysql.connector.connect(
                host= host, 
                user= user, 
                database= wcsDatabase, 
                password= password 
            )

            cursor = connection.cursor()

            sql = "UPDATE host_logs SET type = 'No Upd' where id = %s"

            updateValues = (hostLogId,)

            cursor.execute(sql, updateValues)

            connection.commit()

            cursor.close()
            connection.close()

        except Exception as e:
            print(e)
        finally:
            cursor.close()
            connection.close()


    def getMessageType(self, connection, hostLog):
  
        if GlobalConstants.NewContainer in self.AsciiRequestMessage:
            #self.logMessage("Host to WXS", GlobalConstants.NewContainer, self.AsciiRequestMessage)
            newContainer = Eby_NewContainer.NewContainer(self.libserver)
            result = newContainer.saveNewContainer()
            if result:
                self.update_host_log_as_processed(hostLog[0] , GlobalConstants.NewContainer)
            else:
                #log.dbLog("DatConverter", "Proc Error", self.AsciiRequestMessage)
                print("No update for " + self.AsciiRequestMessage)
                self.update_host_log_as_no_update(hostLog[0])
            return GlobalConstants.NewContainer
        if GlobalConstants.ContainerComplete in self.AsciiRequestMessage:
            #self.logMessage("Host to WXS", GlobalConstants.ContainerComplete, self.AsciiRequestMessage)
            containerComplete = Eby_ContainerComplete.ContainerComplete(self.libserver)
            result = containerComplete.updateContainerAsComplete(connection)
            if result:
                self.update_host_log_as_processed(hostLog[0], GlobalConstants.ContainerComplete)
            else:
                #log.dbLog("DatConverter", "No Upd", self.AsciiRequestMessage)
                print("No update for " + self.AsciiRequestMessage)
                self.update_host_log_as_no_update(hostLog[0])
            return GlobalConstants.ContainerComplete
        if GlobalConstants.AssignmentComplete in self.AsciiRequestMessage:
            #self.logMessage("Host to WXS", GlobalConstants.AssignmentComplete, self.AsciiRequestMessage)
            assignmentComplete = Eby_AssignmentComplete.AssignmentComplete(self.libserver)
            result = assignmentComplete.updateAssignmentComplete(connection)
            assignmentComplete.removeUnneededAssignments(connection)
            if result:
                self.update_host_log_as_processed(hostLog[0] , GlobalConstants.AssignmentComplete)
            else:
                print("No update for " + self.AsciiRequestMessage)
                self.update_host_log_as_no_update(hostLog[0])
            return GlobalConstants.AssignmentComplete
        if GlobalConstants.OrderComplete in self.AsciiRequestMessage:
            #self.logMessage("Host to WXS", GlobalConstants.OrderComplete, self.AsciiRequestMessage)
            orderComplete = Eby_OrderComplete.OrderComplete(self.libserver)
            result = orderComplete.updateOrderComplete(connection)
            if result:
                self.update_host_log_as_processed(hostLog[0] , GlobalConstants.OrderComplete)
            else:
                print("No update for " + self.AsciiRequestMessage)
                self.update_host_log_as_no_update(hostLog[0])
            return GlobalConstants.OrderComplete
        if GlobalConstants.RouteComplete in self.AsciiRequestMessage:
            #self.logMessage("Host to WXS", GlobalConstants.RouteComplete, self.AsciiRequestMessage)
            routeComplete = Eby_RouteComplete.RouteComplete(self.libserver)
            result = routeComplete.updateRouteComplete(connection)
            if result:
                self.update_host_log_as_processed(hostLog[0], GlobalConstants.RouteComplete)
            else:
                print("No update for " + self.AsciiRequestMessage)
                self.update_host_log_as_no_update(hostLog[0])
            return GlobalConstants.RouteComplete
            
      
            


    