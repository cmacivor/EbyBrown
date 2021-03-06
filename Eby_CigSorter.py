"""
Author: Robert J. Ward
Changelog:
-- Version: 1.0 Robert J. Ward
    --- Initial Release
-- Version: 1.1 Yogini Marathe 2020-11-18
    --- Updates with reference to Jira Ticket https://pendant.atlassian.net/browse/WEB-105.
    --- Added new function getNextCodeForPickArea to get the codes in round robin fashion.
    --- Created new table in database wcs.lane_assignments_roundrobin to store last lane assignment code.
    --- Added new function isLaneFull to check if lane to be assigned is full while doing Round Robin (2020-11-20)

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
            #print(exists)
            
            
            if exists == 1:
                query = ("SELECT jurisdiction FROM assignment.dat_master WHERE container_id=\"" + str(TxMessage) + "\"")

                cursor.execute(query)
                extResult = cursor.fetchone()
                if extResult == None:
                    result = 9996
                    #print(result)
                else:
                    result = extResult[0]
                    #print(result)
                    jurisdictionCode = str(result)
                    result = int(result)
                    
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

        if result > 9900:
        
            #Run Jurisdiction API for Lane Assignment
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
            
        else:        
            # updated this part to get code in Round Robin fashion.
            RxMessage = getNextCodeForPickArea(str(TxMessage))
        
               
        # # Create new Stamper DAT file after carton scanned
        # if TxMessage != "No Read" and TxMessage != "Multi-Read" and TxMessage != "Empty String":
        #     if exists == 1:            
        #         ret = datCreate.process(TxMessage)
        #         if ret == "Success":
        #             print("dat file created")
        #             pass
        #         else:
        #             print(ret)
        #             print("dat file create fail")
        #             pass
        #     else:
        #         pass
        # else:
        #     pass
        
        
        # Check for Cig Sorter Pause Request as per Scan Reasons table/page
        
        noRead = scanPause.no_read(TxMessage)
        
        multiRead = scanPause.multi_read(TxMessage)  
        
        noCode = False
        noStampReq = False
        noJurisdiction = False
        laneNotConfigured = False
        noStampFile = False      
         
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
        print("Lane Assignment = " + str(RxMessage))
        
        ret = comm.Read("CigSorter.RxMessage", datatype=STRING)
        laneAssigned = str(ret.Value)
        print("Lane Actual = " + laneAssigned)
        
        
        if TxMessage != "No Read" and TxMessage != "Multi-Read" and TxMessage != "Empty String" and exists == 1:
             
            jurisdictionText = "SELECT pick_area FROM assignment.dat_master WHERE container_id=" + "'" +str(TxMessage) + "'"
            cursor.execute(jurisdictionText)
            result = cursor.fetchone()
            jurisdictionText = result[0]
            #print(jurisdictionText) 
        
        elif TxMessage != "No Read" and TxMessage != "Multi-Read" and TxMessage != "Empty String" and exists == 0:
            jurisdictionText = "--Not in DB--"
        
        else:
            jurisdictionText = "--None--"
        
            
        if pauseBit == False:
            plcLog.dbLog("WXS to PLC", "Lane Assignment", "ReponseID " + str(TxTriggerID) + " | Assigned Carton " + str(TxMessage) + " to Lane " + str(RxMessage) + " with Jurisdiction " + str(jurisdictionText))
        else:
            plcLog.dbLog("WXS to PLC", "Lane Assignment", "ReponseID " + str(TxTriggerID) + " | Sorter Paused for: "+ str(reason))

        return "process - successful"
        
    else:
        return "ValueError: Out of Range"         
        
    
    comm.Close()


def getNextCodeForPickArea(TxMessage):

    pick_area = "SELECT pick_area FROM assignment.dat_master WHERE container_id=" + "'" + str(TxMessage) + "'"
    cursor.execute(pick_area)
    result = cursor.fetchone()
    pick_area = result[0]
    print(pick_area)

    id = "SELECT id FROM wcs.lane_stamp_machines WHERE name=" + "'" + str(pick_area) + "'"
    cursor.execute(id)
    result = cursor.fetchone()
    id = result[0]
    #print(id)

    ## Get all the codes order by code
    lane = "SELECT code FROM wcs.jurisdictions WHERE FIND_IN_SET(" + str(id) + ", lane_stamp_machine_ids) ORDER BY code"
    cursor.execute(lane)
    result = cursor.fetchall()
    lanes = []
    for oneResult in result:
        lanes.append(int(oneResult[0]))

    laneFullCheckRequired = False
    if len(lanes) > 1:
        laneFullCheckRequired = True ## check is required only if there are more than one lanes to be assigned
    lastIndexofLanes = len(lanes) - 1
    #print(lanes)
    # Query the last assigned lane from the database
    lastAssignedLane = "SELECT last_assigned_code FROM wcs.lane_assignments_roundrobin WHERE pick_area = " \
                       + "'" + str(pick_area) + "' AND pick_area_id = " + str(id)
    cursor.execute(lastAssignedLane)
    lastAssignedLane = cursor.fetchone()

    if lastAssignedLane is not None: ## record exists in the database
        lastLane = lastAssignedLane[0]
        if lastLane in lanes:
            #get the index in list and now we need to return next element. The list we get from DB is always in sorted order
            currentAssignedLaneIndex = lanes.index(lastLane)
            #print("last assigned lane : " , lastLane)
            if currentAssignedLaneIndex == lastIndexofLanes: # 0 based index we are at the end of list
                indexToBeAssigned = 0
            else:
                indexToBeAssigned = currentAssignedLaneIndex + 1
            RxMessage = lanes[indexToBeAssigned]
        else:
            RxMessage = lanes[0]

        if laneFullCheckRequired:
            ## check if lane to be assigned is not full.
            if(isLaneFull(RxMessage)):
                print("Lane ", RxMessage, " is full")
                ## cannnot assign the seleted lane hence get next lane
                if indexToBeAssigned == lastIndexofLanes:  # 0 based index we are at the end of list, so pck first one
                    RxMessage = lanes[0]
                else:
                    RxMessage = lanes[indexToBeAssigned + 1]
                print("So assigning ", RxMessage)
        #create update statement to update record in database
        insertUpdateCurrentAssignedLane = "UPDATE wcs.lane_assignments_roundrobin SET last_assigned_code = " + str(RxMessage) + " WHERE" \
                                    + " pick_area = " + "'" + str(pick_area) + "' AND pick_area_id = " + str(id)
    else: #no record exists in the database so return first value and insert record in database
        RxMessage = lanes[0]
        if laneFullCheckRequired:
            ## check if lane to be assigned is not full.
            if(isLaneFull(RxMessage)):
                RxMessage = lanes[1]
        insertUpdateCurrentAssignedLane = "INSERT INTO wcs.lane_assignments_roundrobin (last_assigned_code, pick_area, pick_area_id) " \
                                          "VALUES  (" + str(RxMessage) + " , '" + str(pick_area) + "' ," + str(id) + ")"

    #Write current assigned lane value to the database
    cursor.execute(insertUpdateCurrentAssignedLane)
    connection.commit()
    # Return the current lane value for assignment
    #print("lane to be assigned now : " , str(RxMessage))
    return str(RxMessage)

def isLaneFull(laneNo): # function to read a bit from PLC to ckeck if Lane is Full
    laneFull = False
    if laneNo == 1:
        laneFullBit = "bit04118Lane1Full"
    elif laneNo == 2:
        laneFullBit = "bit04118Lane2Full"
    elif laneNo == 3:
        laneFullBit = "bit04118Lane3Full"
    else:
        pass

    with PLC() as comm:
        comm.IPAddress = plcIP
        ret = comm.Read(laneFullBit, datatype=BOOL)
        laneFull = ret.Value
        comm.Close()

    return laneFull
    

#print("Program started at :  " , datetime.now())
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
        ## for testing the individual function - remove following code after end to end testing
        #getNextCodeForPickArea("FZ7006706-003") ## Baldwin
        ##getNextCodeForPickArea("FZ1006696-001") ## different pick area florida
        #getNextCodeForPickArea("FZ4006705-002") ## TX
        
        
    except Exception as e:
        print(e)
        
        
            
        plcLog.dbLog("WXS to PLC", "Lane Assignment", "ReponseID Exception | " + str(e))
            
        with PLC() as comm:
            comm.Write("CigSorter.RxMessage", "1")
            #comm.Write("CigSorter.RxTriggerID", TxTriggerID)
            comm.Write("CigSorter.TxTrigger", False)
            
            comm.Close()
            
    
        
        
    finally:
        connection.close()


    time.sleep(0.250)


atexit.register(comm.Close())
atexit.register(connection.close())
