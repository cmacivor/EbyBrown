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
    triggerBit = False
    
    with PLC() as comm:
        comm.IPAddress = plcIP
        ret = comm.Read("DockDoorScanner" + door + ".TxTrigger", datatype=BOOL)        
        triggerBit = ret.value

    if triggerBit == False:
        print(triggerBit)

    elif triggerBit == True:
        try:
            connection = mysql.connector.connect(
                host= host, 
                user= user, 
                database= database, 
                password= password 
            )

            cursor = connection.cursor()
        
            print(triggerBit)

            ret = comm.Read("DockDoorScanner" + door + ".TxTriggerID", datatype=INT)
            TxTriggerID = ret.value
            print(TxTriggerID)

            ret = comm.Read("DockDoorScanner" + door + ".TxMessage", datatype=STRING)
            TxMessage = ret.value[5:18]
            print(TxMessage)

            if "NOREAD" in TxMessage:
                TxMessage = "No Read"
            elif "MULTIREAD" in TxMessage:
                TxMessage = "Multi-Read"
            else:
                pass

            print(TxMessage)

            route = ""
            stop = ""
            if TxMessage != "No Read" and TxMessage != "Multi-Read" and TxMessage != "":
                # Mark in dat_master table as stop_scan
                cursor.execute("UPDATE assignment.dat_master SET stop_scan=1 WHERE container_id='" + str(TxMessage) + "';")
                connection.commit()

                route = "SELECT route_no, stop_no FROM assignment.dat_master WHERE container_id='" + str(TxMessage) + "'"
                cursor.execute(route)
                result = cursor.fetchall()                
                route = str(result[0][0])
                stop = str(result[0][1])
                print(route)
                print(stop)

            else:
                pass
            
            currentTimeStamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            reason = ""
            # Log Scan to dashboard_door_scans regardless of read type
            cursor.execute("INSERT INTO wcs.dashboard_door_scans (door_id,barcode,route,stop,reason,created_at,updated_at) VALUES ("+door+","+str(TxMessage)+","+route+","+stop+","+reason+",'"+currentTimeStamp+"','"+currentTimeStamp+"';)")
            connection.commit()

            RxMessage = "Scan Logged"

            # After scan is logged, write received and reset bit
            comm.Write("DockDoorScanner" + door + ".RxMessage", RxMessage)
            comm.Write("DockDoorScanner" + door + ".RxTriggerID", TxTriggerID)
            comm.Write("DockDoorScanner" + door + ".TxTrigger", False)
            print("Scan Logged")

        
        except Exception as e:
            print(e)


    else:
        print("ValueError: Out of Range")









while True:
    door1 = dock_scan_control(1)
    #print(door1)

    time.sleep(0.250)