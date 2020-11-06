"""
Author: Robert J. Ward
Changelog:
-- Version: 1.0 Robert J. Ward
    --- Initial Release

"""

# Imports

import requests
import API_02_HostLog as hostLog
import API_03_httpStatusCodes as httpMessage
import time
import API_04_PLCLog as plcLog
import requests
import python_config
import mysql.connector
import datetime
from pylogix import PLC
import sys
import atexit
#import Eby_DockScanPause as scanPause


config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('wcsdatabase')
password = config.get('password')

logging = python_config.read_logging_config()
auth = logging.get('auth')
domain = logging.get('domain')
plcIP = "10.22.56.34"

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





def dock_scan_control(door):
    door = str(door)
    #print(door)
    triggerBit = False
    
    with PLC() as comm:
        comm.IPAddress = plcIP
        ret = comm.Read("DockDoorScanner" + door + ".TxTrigger", datatype=BOOL)        
        triggerBit = ret.Value

    if triggerBit == False:
        print("Door " + str(door) + " = " + str(triggerBit))

    elif triggerBit == True:
        try:
            connection = mysql.connector.connect(
                host= host, 
                user= user, 
                database= database, 
                password= password 
            )

            cursor = connection.cursor()
        
            print("Door " + str(door) + " = " + str(triggerBit))

            ret = comm.Read("DockDoorScanner" + door + ".TxTriggerID", datatype=INT)
            TxTriggerID = ret.Value
            print(TxTriggerID)

            ret = comm.Read("DockDoorScanner" + door + ".TxMessage", datatype=STRING)
            TxMessage = ret.Value[5:18]
            print(TxMessage)

            reason = ""
            if "NOREAD" in TxMessage:
                TxMessage = "No Read"
                reason = "No Read"
            elif "MULTIREAD" in TxMessage:
                TxMessage = "Multi-Read"
                reason = "Multi-Read"
            else:
                pass

            print(TxMessage)
            
            exists = "SELECT EXISTS (SELECT * FROM assignment.dat_master WHERE container_id=" + "'" + str(TxMessage) + "')"
            cursor.execute(exists)
            result = cursor.fetchone()
            exists = result[0]
            print(exists)

            route = ""
            stop = ""
            if exists == 1:
                
                if TxMessage != "No Read" and TxMessage != "Multi-Read" and TxMessage != "":
                    # Mark in dat_master table as stop_scan
                    cursor.execute("UPDATE assignment.dat_master SET stop_scan=1 WHERE container_id=" + "'" + str(TxMessage) + "'")
                    connection.commit()

                    info = "SELECT route_no, stop_no FROM assignment.dat_master WHERE container_id=" + "'" + str(TxMessage)+ "'"
                    cursor.execute(info)
                    result = cursor.fetchall()                
                    route = str(result[0][0])
                    stop = str(result[0][1])
                    print(route)
                    print(stop)

                else:
                    pass
                
            elif exists == 0 and TxMessage == "No Read":
                reason = "No Read"
            elif exists == 0 and TxMessage == "Multi-Read":
                reason = "Multi-Read"
            else:
                reason = "Not in DB"
            
            currentTimeStamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            
            # Log Scan to dashboard_door_scans regardless of read type
            cursor.execute("INSERT INTO wcs.dashboard_door_scans (door_id,barcode,route,stop,reason,created_at,updated_at) VALUES ("+str(door)+",'"+str(TxMessage)+"','"+route+"','"+stop+"','"+reason+"','"+currentTimeStamp+"','"+currentTimeStamp+"')")
            connection.commit()

            RxMessage = "Scan Logged"

            # After scan is logged, write received and reset bit
            comm.Write("DockDoorScanner" + door + ".RxMessage", RxMessage)
            comm.Write("DockDoorScanner" + door + ".RxTriggerID", TxTriggerID)
            comm.Write("DockDoorScanner" + door + ".TxTrigger", False)
            #print("Scan Logged")
            
            return "Scan Logged"
        
            # Execute Scan Reason Logic
            # TODO Add Function here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # pause = scanPause()
            # print(pause)

        
        except Exception as e:
            print(e)
            
            currentTimeStamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Log Scan to dashboard_door_scans regardless of read type
            cursor.execute("INSERT INTO wcs.dashboard_door_scans (door_id,barcode,route,stop,reason,created_at,updated_at) VALUES ("+str(door)+",'"+str(TxMessage)+"','"+route+"','"+stop+"','"+reason+"','"+currentTimeStamp+"','"+currentTimeStamp+"')")
            connection.commit()
            
            # After scan is logged, write received and reset bit
            comm.Write("DockDoorScanner" + door + ".RxMessage", "NACK")
            comm.Write("DockDoorScanner" + door + ".RxTriggerID", TxTriggerID)
            comm.Write("DockDoorScanner" + door + ".TxTrigger", False)
            print("Error")
            
            return "Error in Processing"


    else:
        print("ValueError: Out of Range")







doors = [1, 2]

while True:
    
    try:
        for door in doors:
            
            doorScan = dock_scan_control(door)
            print(doorScan)
            
    except Exception as e:
        print(e)    

        with PLC() as comm:
            comm.IPAddress = plcIP
            # After scan is logged, write received and reset bit
            comm.Write("DockDoorScanner" + str(door) + ".RxMessage", "NACK")            
            comm.Write("DockDoorScanner" + str(door) + ".TxTrigger", False)
            print("Processing Error")
   
    time.sleep(0.250)
    
    
    
atexit.register(cursor.close)
atexit.register(connection.close())