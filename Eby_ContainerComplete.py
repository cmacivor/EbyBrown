import Eby_MessageProcessor as libserver
import Eby_Message
import mysql.connector 
from datetime import datetime
import time
import python_config
import sys
import API_02_HostLog as hostLog
import traceback
import GlobalFunctions
import Eby_Jurisdiction_Processor
import Eby_NewContainer  

class ContainerComplete:
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.replace("'", "") # libserver.decode('ascii') #libserver.request[:].decode('ascii')
        self.fields = self.populateFields()
        self.MsgSequenceNumber = self.getMessageSequenceNumber()
        self.MessageID = self.fields[1]
        self.ContainerID = self.fields[2]
        self.AssignmentID = self.fields[3]
        self.QCFlag =  self.fields[4] 
        self.CigaretteQuantity = self.getCigaretteQuantity()


    def populateFields(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields

    def getMessageSequenceNumber(self):
        msgSeqNumber =  self.fields[0].replace("x02", "")
        return msgSeqNumber

    def getCigaretteQuantity(self):
        quantity = self.fields[5].replace("x03", "").replace("'", "").replace("\"", "").strip()
        return quantity

        #return self.fields[5]
        # stringList = list(self.fields[5])
        # msgLength = len(stringList)
        # numberWithoutETX = ""
        # for index in range(0, msgLength - 1):
        #     i = stringList[index]
        #     numberWithoutETX += i

        # return numberWithoutETX

    # def getQCFlag(self):
    #     stringList = list(self.fields[4])
    #     msgLength = len(stringList)
    #     numberWithoutETX = ""
    #     for index in range(0, msgLength - 1):
    #         i = stringList[index]
    #         numberWithoutETX += i

    #     #qcflag = self.fields[4].replace('0x3', '')
    #     return numberWithoutETX

   
    def getDatMasterByContainerId(self, containerId):
        config = python_config.read_db_config()

        host = config.get('host')
        user = config.get('user')
        database = config.get('database')
        password = config.get('password')

        try:
            connection = mysql.connector.connect(
                host= host, 
                user= user, 
                database= database, 
                password= password 
            )

            cursor = connection.cursor()

            getByContainerIdSQL = "SELECT * FROM dat_master WHERE container_id = %s" 

            selectData = (containerId,)

        
            cursor.execute(getByContainerIdSQL, selectData)
            
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            return result
        except Exception as e:
            print(e)
            #connection.rollback()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            exceptionMsg = exc_value
            exceptionDetails = ''.join('!! ' + line for line in lines)
        
            GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)
            hostLog.dbLog("Eby_ContainerComplete", "Upd Err", self.AsciiRequestMessage)        
        finally:
            cursor.close()
            connection.close()


    def updateContainerAsComplete(self, connection):
        config = python_config.read_db_config()

        host = config.get('host')
        user = config.get('user')
        database = config.get('database')
        password = config.get('password')

        try:
            connection = mysql.connector.connect(
                host= host, 
                user= user, 
                database= database, 
                password= password 
            )

            cursor = connection.cursor()

            updateContainerSQL = ("UPDATE dat_master SET "
                                "c_comp = %s, "
                                "carton_qty = %s, "
                                "qc_flag = %s, "
                                "updated_at = %s "
                                "WHERE container_id = %s "   

            )

            #currentTimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            currentTimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            updateContainerValues = (1, self.CigaretteQuantity, int(self.QCFlag), currentTimeStamp, self.ContainerID)

        
            cursor.execute(updateContainerSQL , updateContainerValues)
            connection.commit()
            rowcount = cursor.rowcount
            print("Rows updated: " + str(rowcount))
            
            #Web-72
            datMaster = self.getDatMasterByContainerId(self.ContainerID)
            pickCode = datMaster[6][:3]
            if pickCode == "001":
                Eby_Jurisdiction_Processor.process(self.ContainerID)

            cursor.close()
            connection.close()
            if rowcount > 0:
                return True
            else:
                return False
        except Exception as e:
                print(e)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                exceptionMsg = exc_value
                exceptionDetails = ''.join('!! ' + line for line in lines)
            
                GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)
                hostLog.dbLog("Eby_ContainerComplete", "Upd Err", self.AsciiRequestMessage)
                return False
        
        finally:
            cursor.close()
            connection.close()