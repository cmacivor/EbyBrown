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

connection = mysql.connector.connect(
                        host= host, 
                        user= user, 
                        database= database, 
                        password= password 
                    )

cursor = connection.cursor()






def no_read(code, door):
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
    



def multi_read(code, door):
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
    



def code_not_found(code, door):
    # barcode scanned doesn't exist in database (has to be the approved barcode symbology, containing the dash in the correct spot, correct number of characters, etc.)
    
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
        



def route_not_active(code, door):
    # Not an active route for the barcode scanned
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Route Not Active'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
    if enabled == 1:
        currentRoute = "SELECT number FROM wcs.dashboard_routes"+str(door)+ " WHERE route_type=current"
        cursor.execute(currentRoute)
        result = cursor.fetchone()
        currentRoute = result[0]
        #print(currentRoute)
        
        codeRoute = "SELECT route_no FROM assignment.dat_master WHERE container_id=" + "'" + str(code) + "'"
        cursor.execute(codeRoute)
        result = cursor.fetchone()
        codeRoute = result[0]
        #print(codeRoute)
        
        if codeRoute != currentRoute:
            return True
        else:
            return False
    else:
        return False
    
    
    

def door_not_found(code, door):
    # Dock door input is outside the acceptible dock door options (door 1 and 2, but user input door 4 for example)
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Dock Door Not Found'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
    if enabled == 1:
        return False
    else:
        return False
    


    
def route_not_found(code, door):
    # Label scanned belongs to a route not in the database for that day
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Route Not Found'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
    if enabled == 1:
        route = "SELECT route_no FROM assignement.dat_master WHERE container_id=" + "'" + str(code) + "'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = result[0]
        print(route)
        
        activeRoutes = "SELECT route FROM wcs.verify_trailers WHERE dock_door_number=" + "'" + str(door) + "'"
        cursor.execute(activeRoutes)
        results = cursor.fetchall()
        activeRoutes = []        
        for idx, r in enumerate(results):
            activeRoutes.append(results[idx][0])
        #print(activeRoutes)
        
        if route not in activeRoutes:
            return True
        else:
            return False
    else:
        return False
        


    
def stop_not_found(code, door):
    # Stop on route is not found
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Stop Not Found'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
    if enabled == 1:
        route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" + "'" + str(code) + "'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = result[0]
        #print(route)
        
        stop = "SELECT stop_no FROM assignment.dat_master WHERE container_id=" + "'" + str(code) + "'"
        cursor.execute(stop)
        result = cursor.fetchone()
        stop = result[0]
        #print(stop)
        
        date = "SELECT date FROM assignment.dat_master WHERE container_id=" + "'" + str(code) + "'"
        cursor.execute(date)
        result = cursor.fetchone()
        date = result[0]
        #print(date)
        
        return False
    
    else:
        return False
        
        
    
    
def next_route(code, door):
    # First container of next route scanned
    
    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Next Route'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)
    
    if enabled == 1:
        route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" +"'"+ str(code) +"'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = result[0]
        #print(route)

        currentRoute = "SELECT route FROM wcs.dashboard_routes"+"'"+str(door)+"' WHERE route_type='current'"
        cursor.execute(currentRoute)
        result = cursor.fetchone()
        currentRoute = result[0]
        #print(currentRoute)

        if route == currentRoute:
            trailer_pre_verify = "SELECT pre_verify FROM wcs.verify_trailers WHERE route=" +"'"+str(route)+"'"
            cursor.execute(trailer_pre_verify)
            result = cursor.fetchone()
            trailer_pre_verify = result[0]
            #print(trailer_pre_verify)

            if trailer_pre_verify == 0:
                return True
            else:
                return False
            
        else:
            return False
    else:
        return False

        
    
    
def wrong_route(code, door):
    # Container scanned does not belong to the current route or next route

    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Wrong Route'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)

    if enabled == 1:
        route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" +"'"+ str(code) +"'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = result[0]
        #print(route)

        currentRoute = "SELECT route FROM wcs.dashboard_routes"+"'"+str(door)+"' WHERE route_type='current'"
        cursor.execute(currentRoute)
        result = cursor.fetchone()
        currentRoute = result[0]
        #print(currentRoute)

        nextRoute = "SELECT route FROM wcs.dashboard_routes"+"'"+str(door)+"' WHERE route_type='next'"
        cursor.execute(nextRoute)
        result = cursor.fetchone()
        nextRoute = result[0]
        #print(nextRoute)

        if route != currentRoute and route != nextRoute:
            return True
        else:
            return False

    else:
        return False
    



def stop_already_loaded(code, door):
    # Container for the stop that has already been complete is scanned (late container for the stop but belongs to the current route)

    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Stop Already Loaded'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)

    if enabled == 1:
        return False
    else:
        return False



    
def stop_early(code, door):
    # Container for current route but for a later stop than is being loaded currently

    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Stop Early'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)

    if enabled == 1:
        route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" +"'"+ str(code) +"'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = result[0]
        #print(route)

        stop = "SELECT stop_no FROM assignment.dat_master WHERE container_id=" +"'"+ str(code) +"'"
        cursor.execute(stop)
        result = cursor.fetchone()
        stop = result[0]
        #print(stop)

        activeRoute = "SELECT number FROM wcs.dashboard_routes"+str(door)+" WHERE route_type=current"
        cursor.execute(activeRoute)
        result = cursor.fetchone()
        activeRoute = result[0]
        #print(activeRoute)

        activeStop = "SELECT number FROM wcs.dashboard_stops"+str(door)+" WHERE stop_type=current"
        cursor.execute(activeStop)
        result = cursor.fetchone()
        activeStop = result[0]
        #print(activeStop)

        if route == activeRoute and int(stop) < int(activeStop):
            return True
        else:
            return False
        
    else:
        return False


    

def new_stop_dock_picks(code, door):
    # New stop that had containers from the pick area "Dock 1" or "Dock 2". Leave ability to add additional pick areas to qualify under "Dock Picks" category in future (such as seasonal)

    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='New Stop Dock Picks'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)

    if enabled == 1:
        return False
    else:
        return False


    
    
def new_stop_no_dock_picks(code, door):
    # New stop that doesn't have any containers from the specifified "Dock" pick areas

    enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='New Stop No Dock Picks'"
    cursor.execute(enabled)
    result = cursor.fetchone()
    enabled = int(result[0])
    #print(enabled)

    if enabled == 1:
        return False
    else:
        return False
    
    

    
    
    







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
            
            
    
    