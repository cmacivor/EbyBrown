import Eby_MessageProcessor as libserver
import Eby_Message
import sys
import mysql.connector 
from datetime import datetime
import time
import python_config 



class NewContainer:

    #constructor
    def __init__(self, libserver):
        self.libserver = libserver
        self.AsciiRequestMessage = libserver.decode('ascii') #libserver.request[:].decode('ascii')
        self.fields = self.populateFields()
        self.MsgSequenceNumber = self.getMessageSequenceNumber()
        self.MessageID = self.fields[1]
        self.RouteNumber = self.fields[2]
        self.StopNumber = self.fields[3]
        self.ContainerID = self.fields[4]
        self.AssignmentID = self.fields[5]
        self.PickArea = self.fields[6]
        self.PickType = self.fields[7]
        self.Jurisdiction = self.fields[8]
        self.NumberCartons = self.getNumberCartons()  

    def populateFields(self):
        fields = self.AsciiRequestMessage.split('|')
        return fields

    def getMessageSequenceNumber(self):
        msgSeqNumber =  self.fields[0][3:]
        return msgSeqNumber

    def getNumberCartons(self):
        numberCartons = self.fields[9].replace('0x3', '')
        return numberCartons

    def doesNewContainerAlreadyExist(self):
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

        getByContainerIdSQL = "SELECT * FROM dat_master WHERE container_id = %s" 

        selectData = (self.ContainerID,)

        try:
            cursor.execute(getByContainerIdSQL, selectData)
            
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            return result
        except Exception as e:
            print(e)
            connection.rollback()
             #TODO: log error?
             #TODO: log the file that caused the error
        finally:
            cursor.close()
            connection.close()
    

    
    def saveNewContainer(self):
        existingRecord = self.doesNewContainerAlreadyExist()

        if existingRecord is not None:
            #TODO: log this here
            return

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

        addNewContainerSQL = ("INSERT INTO dat_master "
                            "(record_id, container_id, assignment_id, route_no, stop_no, pick_area, pick_type, jurisdiction, carton_qty, status, created_at, updated_at) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        
        currentTimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        
        newContainer = (
            self.MessageID, self.ContainerID, self.AssignmentID, self.RouteNumber, self.StopNumber, self.PickArea, self.PickType, self.Jurisdiction, self.NumberCartons, 'TEST', currentTimeStamp, currentTimeStamp
        )

        try:
            cursor.execute(addNewContainerSQL, newContainer)
            connection.commit()
            
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

           
            

       


    
    
    
    

        


    