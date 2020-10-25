"""
Author: Robert J. Ward
Changelog:
-- Version: 1.0 Robert J. Ward
    --- Initial Release

"""


import time
import API_04_PLCLog as plcLog
import Eby_01_Jurisdiction as jurisdiction
import requests
import python_config
import mysql.connector
from datetime import datetime
from pylogix import PLC
import sys
import Eby_Jurisdiction_Processor as datCreate
sys.path.append("..")




# Data Types
STRUCT = 160
BOOL = 193
SINT = 194
INT = 195
DINT = 196
LINT = 197
USINT = 198
UINT = 199
UDINT = 200
LWORD = 201
REAL = 202
LREAL = 203
DWORD = 211
STRING = 218



config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('wcsdatabase')
password = config.get('password')

logging = python_config.read_logging_config()
auth = logging.get('auth')
domain = logging.get('domain')
plcIP = "10.22.56.34"




while True:
    triggerBit = False

    with PLC() as comm:
        comm.IPAddress = plcIP
        ret = comm.Read("CigSorter.TxTrigger", datatype=BOOL)        
        triggerBit = ret.value               

    if triggerBit == False:
        print(triggerBit)

    elif triggerBit == True:        
        print(triggerBit)
        ret = comm.Read("CigSorter.TxMessage", datatype=STRING)
        if ret.value != None:
            TxMessage = ret.value[5:]
        else:
            TxMessage = "Blank"
        print(TxMessage)
        ret = comm.Read("CigSorter.TxTriggerID", datatype=INT)
        TxTriggerID = ret.value
        print(TxTriggerID)
        plcLog.dbLog("PLC to WXS", "Lane Request", "RequestID " + str(TxTriggerID) + " | Lane Request for " + TxMessage)

        # Query DB Table for jurisdiction from carton_id
        if TxMessage != "NOREAD" and TxMessage != "MULTIREAD" and TxMessage != "Blank":
            try:
                connection = mysql.connector.connect(
                    host= host, 
                    user= user, 
                    database= database, 
                    password= password 
                )

                cursor = connection.cursor()

                query = ("SELECT jurisdiction FROM assignment.dat_master WHERE container_id=\"" + TxMessage + "\"")
                cursor.execute(query)
                extResult = cursor.fetchone()
                if extResult == None:
                    result = 9996
                    print(result)
                else:
                    result = extResult[0]
                    print(result)

            except Exception as e:
                print(e)
                result = 9999
        
            
        
        else:
            if TxMessage == "NOREAD":
                result = 9999
            elif TxMessage == "MULTIREAD":
                result = 9998
            elif TxMessage == "Blank":
                result = 9997
            else:
                result = 9999

        
        # Run Jurisdiction API for Lane Assignment
        ret = jurisdiction.lookup(auth, domain, str(result))
        httpCode = ret[0]
        if httpCode == "200":
            result = ret[1]
            RxMessage = result
        else:
            result = "API Error Code " + httpCode
        print(httpCode)
        print(result)
        
        # If response is out of range send 9999
        if int(RxMessage) < 1 or int(RxMessage) > 9999:
            RxMessage = "9999"
        
        # Create new Stamper DAT file after carton scanned
        ret = datCreate.process(TxMessage)
        if ret == "Success":
            pass
        else:
            print("dat file create fail")


        # Write response to PLC and log message
        tags = [("CigSorter.RxMessage", str(RxMessage)), ("CigSorter.RxTriggerID", TxTriggerID), ("CigSorter.TxTrigger", False)]
        comm.Write("CigSorter.RxMessage", str(RxMessage))
        comm.Write("CigSorter.RxTriggerID", TxTriggerID)
        comm.Write("CigSorter.TxTrigger", False)
        
        plcLog.dbLog("WXS to PLC", "Lane Assignment", "ReponseID " + str(TxTriggerID) + " | httpCode=" + httpCode + " | Assigned Carton " + str(TxMessage) + " to Lane " + str(RxMessage) + " with Jurisdiction " + str(result))

    else:
        print("ValueError: Out of Range")
    
    comm.Close()

    time.sleep(0.250)
