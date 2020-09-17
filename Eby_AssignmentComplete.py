import Eby_MessageProcessor as libserver
import Eby_Message
import re # regular expressions
import mysql.connector 
from datetime import datetime
import time
import python_config 

class AssignmentComplete:
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.decode('ascii') #libserver.request[:].decode('ascii')
        self.fields = self.populateFields()
        self.MsgSequenceNumber = self.getMessageSequenceNumber()
        self.MessageID = self.fields[1]
        self.AssignmentID = self.getAssignmentID()


    def populateFields(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields

    def getMessageSequenceNumber(self):
        msgSeqNumber =  self.fields[0][3:]
        return msgSeqNumber
    
    def getAssignmentID(self):
        assignmentID = self.fields[2].replace('0x3', '')
        return assignmentID

    def updateAssignmentComplete(self):
        config = python_config.read_db_config()

        host = config.get('host')
        user = config.get('user')
        database = config.get('database')
        password = config.get('password')

        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= database, 
            password= password 
        )

        cursor = connection.cursor()

        updateAssignmentSQL = ("UPDATE dat_master SET "
                              "a_comp = %s, "
                              "updated_at = %s "
                              "WHERE assignment_id = %s "   

        )

        currentTimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        updateAssignmentValues = (1, currentTimeStamp, self.AssignmentID)

        try:
            cursor.execute(updateAssignmentSQL, updateAssignmentValues)
            connection.commit()
            rowcount = cursor.rowcount
            print("Rows updated: " + str(rowcount))
            
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print(e)
            connection.rollback()
             #TODO: log error?
             #TODO: log the file that caused the error
            return False
        
        finally:
            cursor.close()
            connection.close()

