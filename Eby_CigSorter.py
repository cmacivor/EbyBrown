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
import atexit
import Eby_CigScanPause as scanPause




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




def cig_sorter():    
    
    
    triggerBit = False

    with PLC() as comm:
        comm.IPAddress = plcIP
        ret = comm.Read("CigSorter.TxTrigger", datatype=BOOL)        
        triggerBit = ret.Value               

    if triggerBit == False:
        #print(triggerBit)
        
        return "False"

    elif triggerBit == True:        
        print(triggerBit)
        ret = comm.Read("CigSorter.TxMessage", datatype=STRING)
        if ret.Value != None:
            TxMessage = ret.Value[5:18]
            if "NO" in TxMessage.upper():
                TxMessage = "No Read"
            elif "MULTI" in TxMessage.upper():
                TxMessage  = "Multi-Read"
            else:
                pass
        
        else:
            TxMessage = "Empty String"
        print(TxMessage)
        ret = comm.Read("CigSorter.TxTriggerID", datatype=INT)
        TxTriggerID = ret.Value
        print(TxTriggerID)
        plcLog.dbLog("PLC to WXS", "Lane Request", "RequestID " + str(TxTriggerID) + " | Lane Request for " + TxMessage)

        # Query DB Table for jurisdiction from carton_id
        jurisdictionCode = "N/A"
        if TxMessage != "No Read" and TxMessage != "Multi-Read" and TxMessage != "Empty String":            
                
            exists = "SELECT EXISTS (SELECT * FROM assignment.dat_master WHERE container_id=" + "'" + str(TxMessage) + "')"
            cursor.execute(exists)
            result = cursor.fetchone()
            exists = result[0]
            print(exists)
            
            
            if exists == 1:
                query = ("SELECT jurisdiction FROM assignment.dat_master WHERE container_id=\"" + str(TxMessage) + "\"")

                cursor.execute(query)
                extResult = cursor.fetchone()
                if extResult == None:
                    result = 9996
                    print(result)
                else:
                    result = extResult[0]
                    print(result)
                    jurisdictionCode = str(result)
                    
            else:
                result = 9996
            
        
            
        
        else:
            if TxMessage == "No Read":
                result = 9999
            elif TxMessage == " Multi-Read":
                result = 9998
            elif TxMessage == "Empty String":
                result = 9997
            else:
                result = 9999

        
        # Run Jurisdiction API for Lane Assignment
        RxMessage = ""       
        ret = jurisdiction.lookup(auth, domain, str(result))
        httpCode = ret[0]
        if httpCode == "200":
            result = ret[1]
            RxMessage = result
        else:
            result = "API Error Code " + httpCode
            RxMessage  = 0
        #print(httpCode)
        print(result)
        
               
        # Create new Stamper DAT file after carton scanned
        if exists == 1:
            if TxMessage != "No Read" and TxMessage != "Multi-Read" and TxMessage != "Empty String":
                ret = datCreate.process(TxMessage)
                if ret == "Success":
                    print("dat file created")
                    pass
                else:
                    print(ret)
                    print("dat file create fail")
                    pass
            else:
                pass
        else:
            pass
        
        
        # Check for Cig Sorter Pause Request as per Scan Reasons table/page
        
        noRead = scanPause.no_read(TxMessage)
        
        multiRead = scanPause.multi_read(TxMessage)        
         
        if TxMessage != "No Read" and TxMessage != "Multi-Read" and TxMessage != "Empty String":
            
            noCode = scanPause.code_not_found(TxMessage)
            
            if noCode == False:
            
                noStampReq = scanPause.stamp_not_required(TxMessage)
                
                noJurisdiction = scanPause.jurisdiction_not_found(TxMessage)
                
                if noJurisdiction == False:
                    
                    laneNotConfigured = scanPause.jurisdiction_lane_not_configured(TxMessage)
                    
                else:
                    laneNotConfigured = False
                    
                
                noStampFile = scanPause.stamp_file_not_found(TxMessage)
                
            else:
                noStampReq = False
                noJurisdiction = False                
                noStampFile = False
        
            
        else:
            noCode = False
            
            
        if noRead or multiRead or noCode or noStampReq or noJurisdiction or laneNotConfigured or noStampFile == True:
            comm.Write("wxsCigSorterPause", True)
            if noRead == True:
                reason = "No Read"
            elif multiRead == True:
                reason = "Multi-Read"
            elif noCode == True:
                reason = "Container_id Not in Database"
            elif noStampReq == True:
                reason = "No Stamp Required"
            elif noJurisdiction == True:
                reason = "No Jurisdiction Found"
            elif laneNotConfigured == True:
                reason = "No Lane Assigned"
            elif noStampFile == True:
                reason = "Stamp File not Created"
        else:
            comm.Write("wxsCigSorterPause", False)
        
        ret = comm.Read("wxsCigSorterPause", datatype=BOOL)
        pauseBit = ret.Value
                
        print("noRead= " + str(noRead))
        print("multiRead= " + str(multiRead))
        print("noCode= " + str(noCode))
        print("noStampReq= " + str(noStampReq))
        print("noJurisdiction= " + str(noJurisdiction))
        print("laneNotConfigured= " + str(laneNotConfigured))
        print("noStampFile= " + str(noStampFile))
        print("pauseBit= " + str(pauseBit))

        # Write response to PLC and log message            
        comm.Write("CigSorter.RxMessage", str(RxMessage))
        comm.Write("CigSorter.RxTriggerID", TxTriggerID)
        comm.Write("CigSorter.TxTrigger", False)
        
        if pauseBit == False:
            plcLog.dbLog("WXS to PLC", "Lane Assignment", "ReponseID " + str(TxTriggerID) + " | httpCode=" + httpCode + " | Assigned Carton " + str(TxMessage) + " to Lane " + str(RxMessage) + " with Jurisdiction " + str(jurisdictionCode))
        else:
            plcLog.dbLog("WXS to PLC", "Lane Assignment", "ReponseID " + str(TxTriggerID) + " | Sorter Paused for: "+ str(reason))

        return "process - successful"
        
    else:
        return "ValueError: Out of Range"         
        
    
    comm.Close()
    

    
    
    


while True:
    
    try:
        connection = mysql.connector.connect(
                        host= host, 
                        user= user, 
                        database= database, 
                        password= password 
                    )

        cursor = connection.cursor()
        
        
        cigSorter = cig_sorter()
        print(cigSorter)

        connection.close()
        
        
    except Exception as e:
        print(e)
        
        
            
        plcLog.dbLog("WXS to PLC", "Lane Assignment", "ReponseID Exception | " + str(e))
            
        with PLC() as comm:
            comm.Write("CigSorter.RxMessage", "1")
            #comm.Write("CigSorter.RxTriggerID", TxTriggerID)
            comm.Write("CigSorter.TxTrigger", False)
            
            comm.Close()
            
    
        connection.close()


    time.sleep(0.250)

    
    
atexit.register(comm.Close())
atexit.register(connection.close())
