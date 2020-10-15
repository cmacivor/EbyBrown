import Eby_MessageProcessor as libserver
import Eby_Message
import re # regular expressions
import mysql.connector 
from datetime import datetime
import time
import python_config
import sys
import API_02_HostLog as hostLog
import traceback
import GlobalFunctions 

class RouteComplete:
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.replace("'", "") #libserver.decode('ascii') #libserver.request[:].decode('ascii')
        self.fields = self.populateFields()
        self.MsgSequenceNumber = self.getMessageSequenceNumber()
        self.MessageID = self.fields[1]
        self.Route = self.getRoute()


    def populateFields(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields

    def getMessageSequenceNumber(self):
        msgSeqNumber =  self.fields[0][3:]
        return msgSeqNumber

    def getRoute(self):
        # stringList = list(self.fields[2])
        # msgLength = len(stringList)
        # numberWithoutETX = ""
        # for index in range(0, msgLength - 1):
        #     i = stringList[index]
        #     numberWithoutETX += i

        route = self.fields[2].replace('x03', '')
        return route
        #return numberWithoutETX
    
    def updateRouteComplete(self, connection):
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

            updateRouteCompleteSQL = ("UPDATE dat_master SET "
                                "r_comp = %s, "
                                "updated_at = %s "
                                "WHERE route_no = %s "  

            )

            currentTimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            updateRouteValues = (1, currentTimeStamp, self.Route)

            cursor.execute(updateRouteCompleteSQL, updateRouteValues)
            connection.commit()
            rowcount = cursor.rowcount
            print("Rows updated: " + str(rowcount))
            
            cursor.close()
            connection.close()
            if rowcount > 0:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            #connection.rollback()

            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            exceptionMsg = exc_value.msg
            exceptionDetails = ''.join('!! ' + line for line in lines)
          
            GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)
            hostLog.dbLog("DatConverter", "Upd Err", self.AsciiRequestMessage)
            return False
        
        finally:
            cursor.close()
            connection.close()