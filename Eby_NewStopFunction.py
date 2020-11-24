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
import Eby_02_DashboardModal as modal


config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('wcsdatabase')
password = config.get('password')

logging = python_config.read_logging_config()
auth = logging.get('auth')
domain = logging.get('domain')
plcIP = "10.22.56.34"




display_time = "30"
latch_time = "3600"










def new_stop_dock_picks(door):
    # New stop that had containers from the pick area "Dock 1" or "Dock 2". Leave ability to add additional pick areas to qualify under "Dock Picks" category in future (such as seasonal)
    
    try:
        
        connection = mysql.connector.connect(
                         host= host, 
                         user= user, 
                         database= database, 
                         password= password 
                     )

        cursor = connection.cursor()

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='New Stop Dock Picks'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        #print(enabled)
        
        currentRoute = "SELECT number FROM wcs.dashboard_routes"+str(door)+" WHERE route_type='current'"
        cursor.execute(currentRoute)
        result = cursor.fetchone()
        currentRoute = int(result[0])
        #print(currentRoute)
        
        date = "SELECT date FROM wcs.dashboard_routes"+str(door)+" WHERE route_type='current'"
        cursor.execute(date)
        result = cursor.fetchone()
        date = result[0]
        #print(date)
        
        lastStop = "SELECT number FROM wcs.dashboard_stops"+str(door)+" WHERE stop_type='last'"
        cursor.execute(lastStop)
        result = cursor.fetchone()
        lastStop = int(result[0])
        #print(lastStop)
        
        currentStop = "SELECT number FROM wcs.dashboard_stops"+str(door)+" WHERE stop_type='current'"
        cursor.execute(currentStop)
        result = cursor.fetchone()
        currentStop = int(result[0])
        #print(currentStop)        
        
        
        dockPicks = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" +"'"+str(currentRoute)+"' AND stop_no=" +"'"+str(
                        currentStop)+"' AND date=" +"'"+str(date)+"' AND pick_area LIKE '%dock%'"            
        cursor.execute(dockPicks)
        results = cursor.fetchone()            
        dockPicks = int(results[0])
        #print(dockPicks)

        if enabled == 1:          
            
            if currentStop != lastStop and dockPicks > 0:                
                
                id = modal.pop_up("<br>"+str(currentRoute)+"-"+str(currentStop)+"<br>"+str(dockPicks)+"<br>DOCK PICKS<br><br>", "#FE0400", " #FAFE00", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id="+"'"+str(id)+"' WHERE door_no="+"'"+str(door)+"';")
                cursor.execute("UPDATE wcs.dashboard_stops"+str(door)+" SET number="+"'"+str(currentStop)+"' WHERE stop_type='last'")
                cursor.execute("UPDATE assignment.dat_master SET dashboard_map=1, stop_scan=1 WHERE route_no="+"'"+str(currentRoute)+"' AND stop_no="+"'"+
                                str(currentStop)+"' AND date="+"'"+str(date)+"' AND pick_area LIKE '%dock%'")  
                connection.commit()
                return True
            else:
                return False
                    
            
            
        else:
            if currentStop != lastStop and dockPicks > 0:          
                
                id = modal.pop_up("<br>"+str(currentRoute)+"-"+str(currentStop)+"<br>"+str(dockPicks)+"<br>DOCK PICKS<br><br>", "#FE0400", " #FAFE00", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id="+"'"+str(id)+"' WHERE door_no="+"'"+str(door)+"';")
                cursor.execute("UPDATE wcs.dashboard_stops"+str(door)+" SET number="+"'"+str(currentStop)+"' WHERE stop_type='last'")
                cursor.execute("UPDATE assignment.dat_master SET dashboard_map=1, stop_scan=1 WHERE route_no="+"'"+str(currentRoute)+"' AND stop_no="+"'"+
                                str(currentStop)+"' AND date="+"'"+str(date)+"' AND pick_area LIKE '%dock%'") 
                connection.commit()
            return False
        
    except Exception as e:
        print(e)
        
    finally:
        connection.close()


    
    
def new_stop_no_dock_picks(door):
    # New stop that doesn't have any containers from the specifified "Dock" pick areas
    
    try:
        
        connection = mysql.connector.connect(
                         host= host, 
                         user= user, 
                         database= database, 
                         password= password 
                     )

        cursor = connection.cursor()

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='New Stop No Dock Picks'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        #print(enabled)
        
        currentRoute = "SELECT number FROM wcs.dashboard_routes"+str(door)+" WHERE route_type='current'"
        cursor.execute(currentRoute)
        result = cursor.fetchone()
        currentRoute = int(result[0])
        #print(currentRoute)
        
        date = "SELECT date FROM wcs.dashboard_routes"+str(door)+" WHERE route_type='current'"
        cursor.execute(date)
        result = cursor.fetchone()
        date = result[0]
        #print(date)
        
        lastStop = "SELECT number FROM wcs.dashboard_stops"+str(door)+" WHERE stop_type='last'"
        cursor.execute(lastStop)
        result = cursor.fetchone()
        lastStop = int(result[0])
        #print(lastStop)
        
        currentStop = "SELECT number FROM wcs.dashboard_stops"+str(door)+" WHERE stop_type='current'"
        cursor.execute(currentStop)
        result = cursor.fetchone()
        currentStop = int(result[0])
        #print(currentStop)         
        
        
        dockPicks = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" +"'"+str(currentRoute)+"' AND stop_no=" +"'"+str(
                        currentStop)+"' AND date=" +"'"+str(date)+"' AND pick_area LIKE '%dock%'"            
        cursor.execute(dockPicks)
        results = cursor.fetchone()            
        dockPicks = int(results[0])
        #print(dockPicks)

        if enabled == 1:          
            
            if currentStop != lastStop and dockPicks == 0:                
                
                id = modal.pop_up("<br>"+str(currentRoute)+"-"+str(currentStop)+"<br>NO DOCK<br>PICKS<br><br>", "#000000", " #FAFE00", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id="+"'"+str(id)+"' WHERE door_no="+"'"+str(door)+"';")
                cursor.execute("UPDATE wcs.dashboard_stops"+str(door)+" SET number="+"'"+str(currentStop)+"' WHERE stop_type='last'")                
                connection.commit()
                return True
            else:
                return False                
            
            
        else:
            if currentStop != lastStop and dockPicks == 0:                 
                
                id = modal.pop_up("<br>"+str(currentRoute)+"-"+str(currentStop)+"<br>NO DOCK<br>PICKS<br><br>", "#000000", " #FAFE00", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id="+"'"+str(id)+"' WHERE door_no="+"'"+str(door)+"';")
                cursor.execute("UPDATE wcs.dashboard_stops"+str(door)+" SET number="+"'"+str(currentStop)+"' WHERE stop_type='last'")                
                connection.commit()
            return False
        
    except Exception as e:
        print(e)
        
    finally:
        connection.close()




doors = [1, 2]

while True:

    try:

        with PLC() as comm:
            comm.IPAddress = plcIP

        for d in doors:
            newStop_withPicks = new_stop_dock_picks(d)
            print("New Stop with Picks = " +str(newStop_withPicks))

            newStop_noPicks = new_stop_no_dock_picks(d)
            print("New Stop No Picks = " +str(newStop_noPicks))

            if newStop_withPicks == True or newStop_noPicks == True:
                comm.Write("wxsDoor" + str(d) + "Pause", True)
            else:
                comm.Write("wxsDoor" + str(d) + "Pause", False)

        
    except Exception as e:
        print(e)

    
    time.sleep(2)



atexit.register(connection.close())
    
    
