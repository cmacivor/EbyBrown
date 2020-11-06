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




def no_read(code):
    #Barcode missing or otherwise unable to be read

    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='No Read'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)

    if enabled == 1:
        if "no" in code.lower():
            return True
        else:
            return False
    else:
        return False
    
    

def multi_read(code):
    #Two barcodes read at same time

    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Multi Read'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
    if enabled == 1:
        if "multi" in code.lower():
            return True
        else:
            return False
    else:
        return False
    


def code_not_found(code):
    #barcode scanned doesn't exist in database (has to be the approved barcode symbology, containing the dash in the correct spot, correct number of characters, etc.)
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Barcode Not Found'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
    if enabled == 1:
        exists = "SELECT EXISTS (SELECT * FROM assignment.dat_master WHERE container_id=" + "'" + str(code) + "')"
        cursor.execute(exists)
        result = cursor.fetchone()
        exists = result[0]
        #print(exists)
        
        if exists == 1:
            return True
        else:
            return False
    else:
        return False
        

def route_not_active(code):
    #Stuff
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Route Not Active'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
    
    

def door_not_found(code):
    #Stuff
    test = test
    
    
def route_not_found(code):
    #Stuff
    test = test
    
    
def stop_not_found(code):
    #Stuff
    test = test
    
    
def next_route(code):
    #Stuff
    test = test
    
    
def wrong_route(code):
    #Stuff
    test = test
    

def stop_already_loaded(code):
    #Stuff
    test = test
    
    
def stop_early(code):
    #Stuff
    test = test
    

def new_stop_dock_picks(code):
    #Stuff
    test = test
    
    
def new_stop_no_dock_picks(code):
    #Stuff
    test = test
    
    

    
    
    







def door_pause(code):
    
    
    try:
        connection = mysql.connector.connect(
                host= host, 
                user= user, 
                database= database, 
                password= password 
            )

        cursor = connection.cursor()
        
    
    

        
        
    except Exception as e:
        print(e)
            
            
    
    