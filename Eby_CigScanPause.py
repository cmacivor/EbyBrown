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
import Eby_01_Jurisdiction as jurisdiction
import os  



config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('wcsdatabase')
password = config.get('password')

logging = python_config.read_logging_config()
auth = logging.get('auth')
domain = logging.get('domain')
plcIP = "10.22.56.34"



connection = mysql.connector.connect(
                        host= host, 
                        user= user, 
                        database= database, 
                        password= password 
                    )

cursor = connection.cursor()



def no_read(code):
    #Barcode missing or otherwise unable to be read

    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Cigarette Module' AND reason='No Read'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    print("no read enabled= "+str(enabled))

    if enabled == 1:
        if "no" in code.lower():
            return True
        else:
            return False
    else:
        return False
    

def multi_read(code):
    #Two barcodes read at same time

    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Cigarette Module' AND reason='Multi Read'"
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
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Cigarette Module' AND reason='Barcode Not Found'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    print(enabled)
    
    if enabled == 1:
        exists = "SELECT EXISTS (SELECT * FROM assignment.dat_master WHERE container_id=" + "'" + str(code) + "')"
        cursor.execute(exists)
        result = cursor.fetchone()
        exists = result[0]
        print(exists)
        
        if exists == 0:
            return True
        else:
            return False
    else:
        return False
    
    
def stamp_not_required(code):
    #Stuff
    return False
    

def jurisdiction_not_found(code):
    #barcode scanned doesn't exist in database (has to be the approved barcode symbology, containing the dash in the correct spot, correct number of characters, etc.)
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Cigarette Module' AND reason='Jurisdiction Not Found'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
    if enabled == 1:
        exists = "SELECT jurisdiction FROM assignment.dat_master WHERE container_id=" + "'" + str(code) + "'"
        cursor.execute(exists)
        result = cursor.fetchone()
        exists = result[0]
        #print(exists)
        
        if exists.isspace() == True:
            return True
        else:
            return False
    else:
        return False
    

def jurisdiction_lane_not_configured(code):
    # Jurisdiction read from file not configured to divert to any lane
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Cigarette Module' AND reason='Jurisdiction Lane Not Configured'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
        
    if enabled == 1:
        
        juris = "SELECT jurisdiction FROM assignment.dat_master WHERE container_id=" + "'" + str(code) + "'"
        cursor.execute(juris)
        result = cursor.fetchone()
        juris = result[0]
        #print(juris)
        
        ret = jurisdiction.lookup(auth, domain, str(juris))
        httpCode = ret[0]
        if httpCode == "200":
            lane = int(ret[1])
            
            if lane == 1 or lane == 2 or lane == 3:
                return False
            else:
                return True
            
        else:
            return True
    else:
        return False
    
    
def stamp_file_not_found(code):
    # No file for stamping found on WCS server for United Slicone
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Cigarette Module' AND reason='Stamp File Not Found'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
    if enabled == 1:
        if os.path.exists("D:\\Downloads\\UnitedSilicone\\" + str(code) + ".DAT") == True:
            return False
        else:
            return True
    else:
        return False
        
    
    
   


