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


class OrderComplete:
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.decode('ascii') #libserver.request[:].decode('ascii')
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

    def updateOrderComplete(self):
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

            updateOrderCompleteSQL = ("UPDATE dat_master SET "
                                "o_comp = %s, "
                                "updated_at = %s "
                                "WHERE route_no = %s "
                                "AND stop_no = %s"   

            )

            currentTimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            updateOrderValues = (1, currentTimeStamp, self.Route, self.Stop)

        
            cursor.execute(updateOrderCompleteSQL, updateOrderValues)
            connection.commit()
            rowcount = cursor.rowcount
            print("Rows updated: " + str(rowcount))
            
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
          
            GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails) 
            return False
        
        finally:
            cursor.close()
            connection.close()