import Eby_MessageProcessor as libserver
import Eby_Message
import sys
import mysql.connector 
from datetime import datetime
import time
import python_config
import API_02_HostLog as hostLog
import traceback
import GlobalFunctions 



class NewContainer:

    #constructor
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.replace("'", "") #libserver.decode('ascii') #libserver.request[:].decode('ascii')
        self.fields = self.populateFields()
        self.MsgSequenceNumber = self.getMessageSequenceNumber()
        self.MessageID = self.fields[1]
        self.RouteNumber = self.fields[2] if self.fields[2] else ""
        self.StopNumber = self.fields[3] if self.fields[3] else ""
        self.ContainerID = self.fields[4] if self.fields[4] else ""
        self.AssignmentID = self.fields[5] if self.fields[5] else ""
        self.PickArea = self.fields[6] if self.fields[6] else ""
        self.PickType = self.fields[7] if self.fields[7] else ""
        self.Jurisdiction = self.fields[8] if self.fields[8] else ""
        self.NumberCartons = self.getNumberCartons()
        self.loggingConfig = python_config.read_logging_config()  

    def populateFields(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields

    def getMessageSequenceNumber(self):
        msgSeqNumber =  self.fields[0].replace("x02", "")
        return msgSeqNumber

    def getNumberCartons(self):
        numberCartons = self.fields[9].replace("x03", "").strip()
        return numberCartons
        # try:
        #     stringList = list(self.fields[9])
        #     msgLength = len(stringList)
        #     numberWithoutETX = ""
        #     for index in range(0, msgLength - 1):
        #         i = stringList[index]
        #         numberWithoutETX += i
        #     return numberWithoutETX
        # except IndexError:
        #     return ""

    def doesNewContainerAlreadyExist(self):
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

            selectData = (self.ContainerID,)

        
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
            exceptionMsg = exc_value.msg
            exceptionDetails = ''.join('!! ' + line for line in lines)
          
            GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)          
        finally:
            cursor.close()
            connection.close()

    

    
    def saveNewContainer(self):
        loggingConfig = python_config.read_logging_config()
        enabled = loggingConfig.get('enabled')
        auth = loggingConfig.get('auth')
        domain = loggingConfig.get('domain')

        existingRecord = self.doesNewContainerAlreadyExist()

        if existingRecord is not None:
            if enabled == "1":                                                              #the ContainerID
                hostLog.log(auth, domain, "HOST to WXS", "Dupl", existingRecord[2])
            return

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

            addNewContainerSQL = ("INSERT INTO dat_master "
                                "(record_id, container_id, assignment_id, route_no, stop_no, pick_area, pick_type, jurisdiction, carton_qty, c_comp, a_comp, o_comp, r_comp, assign_name, status, created_at, updated_at) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            
            currentTimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            
            newContainer = (
                self.MessageID, self.ContainerID, self.AssignmentID, self.RouteNumber, self.StopNumber, self.PickArea, self.PickType, self.Jurisdiction, self.NumberCartons, 0, 0, 0, 0, 'SOCKET', '', currentTimeStamp, currentTimeStamp
            )

            cursor.execute(addNewContainerSQL, newContainer)
            connection.commit()
            rowcount = cursor.rowcount
            print("Rows inserted: " + str(rowcount))

            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print(e)
            #connection.rollback()         
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            exceptionMsg = exc_value.msg
            exceptionDetails = ''.join('!! ' + line for line in lines)
            # print(''.join('!! ' + line for line in lines))
            GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)  
            hostLog.dbLog("DatConverter", "Upd Err", self.AsciiRequestMessage)
            return False
        
        finally:
            cursor.close()
            connection.close()

           
            

       


    
    
    
    

        


    