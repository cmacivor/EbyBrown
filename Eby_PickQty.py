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


config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('wcsdatabase')
password = config.get('password')




def update_pick_qty():
    try:
        connection = mysql.connector.connect(
        host= host, 
        user= user, 
        database= database, 
        password= password 
        )

        cursor = connection.cursor()
    
    
        rows = "SELECT id FROM wcs.route_statuses"
        cursor.execute(rows)
        result = cursor.fetchall()
        rows = []
        for i in result:
            rows.append(i[0])
        #print(rows)
        
        
        for row in rows:
            route = "SELECT route FROM wcs.route_statuses WHERE id=" + str(row)
            cursor.execute(route)
            result = cursor.fetchone()
            route = result[0]
            #print(route)
            
            date = "SELECT date FROM wcs.route_statuses WHERE id=" + str(row)
            cursor.execute(date)
            result = cursor.fetchone()
            date = result[0]
            #print(date)
            
            pick_qty = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "'"    
            cursor.execute(pick_qty)
            result = cursor.fetchone()
            pick_qty = result[0]
            #print(pick_qty)
            
            cursor.execute("UPDATE wcs.route_statuses SET pick_qty=" + str(pick_qty) + " WHERE id=" + str(row) + ";")
            connection.commit()
    
    
        return "pick quantites updated for " + str(len(rows)) + " route(s)"
    
    

    except Exception as e:
        print(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)
        
        

while True:
    updatePickQty = update_pick_qty()
    print(updatePickQty)

    time.sleep(1)
    