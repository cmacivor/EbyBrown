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
from datetime import datetime
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




def door_enabled(door):

    # Check table for status of Enabled/Disabled and Normal/Override


    # Write values into PLC



def door_active(door):
    
    # Check verify_trailers table for active route
    routes = "SELECT route FROM wcs.verify_trailers"
    cursor.execute(routes)
    result = cursor.fetchall()
    routes = []
    for r in result:
        routes.append(r[0])
    #print(routes)

    doorActive = False
    for route in routes:
        print("")
        #print(route)

        pre_verify = "SELECT pre_verify FROM wcs.verify_trailers WHERE route=" + str(route)
        cursor.execute(pre_verify)
        result = cursor.fetchone()
        pre_verify = result[0]
        #print(pre_verify)
        
        status = "SELECT status FROM wcs.verify_trailers WHERE route=" + str(route)
        cursor.execute(status)
        result = cursor.fetchone()
        status = result[0]
        #print(status)

        if pre_verify == 1 and status != "Complete":
            doorActive = True
            break
        else:
            doorActive = False
    
    print(doorActive)
    if doorActive == True:
        with PLC() as comm:
            comm.IPAddress = plcIP
            comm.Write("wxsDoor" + str(door) + "Control", 1)
            
    elif doorActive != True:
        with PLC() as comm:
            comm.IPAddress = plcIP
            comm.Write("wxsDoor" + str(door) + "Control", 0)
    
    ret = comm.Read("wxsDoor" + str(door) + "Control", datatype=INT)
    print(ret.value)
    comm.Close()


    return "Executed"










# Connect to DB and run functions

doors = [1, 2]

while True:
    try:
        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= database, 
            password= password 
        )

        cursor = connection.cursor()



        for door in doors:
            doorEnabled = door_enabled(door)
            print("Door " + str(door) + " Enabled = " doorEnabled)

            doorActive = door_active(door)
            print("Door " + str(door) + " Active = " doorActive)

            
        




    except Exception as e:
            print(e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            exceptionMsg = exc_value.msg
            exceptionDetails = ''.join('!! ' + line for line in lines)
            
            GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)

    
    time.sleep(3)



atexit.register(cursor.close)
atexit.register(connection.close())