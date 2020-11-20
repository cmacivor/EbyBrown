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
import Eby_DockScanPause as scanPause
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
        return "Door " + str(door) + " = " + str(triggerBit)

    elif triggerBit == True:
        
        
        print("Door " + str(door) + " = " + str(triggerBit))

        ret = comm.Read("DockDoorScanner" + door + ".TxTriggerID", datatype=INT)
        TxTriggerID = ret.Value
        print(TxTriggerID)

        ret = comm.Read("DockDoorScanner" + door + ".TxMessage", datatype=STRING)
        TxMessage = ret.Value[5:18]
        #print(TxMessage)

        reason = ""
        if "NO" in TxMessage.upper():
            TxMessage = "No Read"
            reason = "No Read"
        elif "MULTI" in TxMessage.upper():
            TxMessage = "Multi-Read"
            reason = "Multi-Read"
        else:
            pass

        print(TxMessage)
        
        exists = "SELECT EXISTS (SELECT * FROM assignment.dat_master WHERE container_id=" + "'" + str(TxMessage) + "')"
        cursor.execute(exists)
        result = cursor.fetchone()
        exists = result[0]
        if exists == 1:
            print("exists in DB")
        else:
            print("does not exist in DB")

        route = ""
        stop = ""
        reason = "To Dock Door"
        if exists == 1:
            
            if TxMessage != "No Read" and TxMessage != "Multi-Read" and TxMessage != "":
                # Mark in dat_master table as stop_scan
                cursor.execute("UPDATE assignment.dat_master SET stop_scan=1, dashboard_map=1 WHERE container_id=" + "'" + str(TxMessage) + "'")
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
            
        ## if No Read then increase No Read by 1    
        if TxMessage == "No Read":
            currentNoRead = "SELECT door_no_read FROM wcs.dashboard_routes"+str(door)+ " WHERE route_type='current'"  
            #print(currentNoRead)          
            cursor.execute(currentNoRead)
            result = cursor.fetchone()
            currentNoRead = result[0]
            print(currentNoRead)
            
            updatedNoRead = currentNoRead + 1
            cursor.execute("UPDATE wcs.dashboard_routes" +str(door)+" SET door_no_read='" +str(updatedNoRead)+ "' WHERE route_type='current';")
            cursor.execute("UPDATE wcs.dashboard_stops" +str(door)+" SET door_no_read='" +str(updatedNoRead)+ "' WHERE stop_type='current';")
            connection.commit()
            
        ## Check if Full Verify is needed
                
        if exists == 1 and TxMessage != "No-Read" and TxMessage != "Multi-Read":
            route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" +"'"+str(TxMessage)
            cursor.execute(route)
            result = cursor.fetchone()
            route = result[0]
            #print(result)
            
            currentRoute = "SELECT number FROM wcs.dashboard_routes" +"'"+str(door)+"' WHERE route_type='current'"
            cursor.execute(currentRoute)
            result = cursor.fetchone()
            currentRoute = result[0]
            #print(currentRoute)
            
            if route == currentRoute:
                cursor.execute("UPDATE wcs.trailer_verify SET full_verify=1 WHERE route=" +"'"+str(route)+"' AND pre_verify=1")
                connection.commit()
        
        
        
        ## End Full verify Check
        
        
        ## Begin Previous Stop Check
        
        stop_switch = False
        
        if exists == 1 and TxMessage != "No-Read" and TxMessage != "Multi-Read":
            
            scan_stop = "SELECT stop_no FROM assignment.dat_master WHERE container_id=" +"'"+str(TxMessage)+"'"
            cursor.execute(scan_stop)
            result = cursor.fetchone()
            scan_stop = result[0]
            #print(scan_stop)
            
            scan_date = "SELECT stop_no FROM assignment.dat_master WHERE container_id=" +"'"+str(TxMessage)+"'"
            cursor.execute(scan_date)
            result = cursor.fetchone()
            scan_date = result[0]
            #print(scan_date)
            
            allStops = "SELECT stop_no FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(scan_date) + "'"
            cursor.execute(allStops)
            result = cursor.fetchall()
            resultList = []
            stopsList = []
            for i in result:
                if int(i[0]) not in resultList:
                    resultList.append(int(i[0]))
                    stopsList = sorted(resultList, reverse=True)
            #print(stopsList)
            
            currentStop = "SELECT number FROM wcs.dashboard_stops" + str(door) + " WHERE stop_type = 'current'"
            cursor.execute(currentStop)
            result = cursor.fetchone()
            currentStop = result[0]
            #print(currentStop)
            
            currentStop_index = allStops.index(currentStop)
            
            # Make sure this is not the last stop on a route
            if currentStop_index != (len(allStops)-1):
                next_stop = allStops[currentStop_index+1]               
                
                # Check if the scanned stop is equal to the next stop; if so, copy current_stop to previous_stop and mark remaining unscanned as late
                if scan_stop == next_stop:
                    #dashboard.previous_stop(door)
                    
                    cursor.execute("UPDATE assignment.dat_master SET late=1, dashboard_map=1 WHERE route_no=" +"'"+str(route)+"' date=" +"'"+str(scan_date)+"' AND stop_no=" +"'"+str(scan_stop)
                                   +"' AND stop_scan=0")
                    connection.commit()
                    
                    stop_switch = True
                    
            else:
                pass
            
             
        
        ## End Previous Stop Check
        
        ## Check for current stop having lates and switch to next stop
        
        # if stop_switch == True:
            
        #     if currentStop_index != (len(allStops)-1):
                
                
        
        
        currentTimeStamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

        
        # Log Scan to dashboard_door_scans regardless of read type
        cursor.execute("INSERT INTO wcs.dashboard_door_scans (door_id,barcode,route,stop,reason,created_at,updated_at) VALUES ("+str(door)+",'"+str(TxMessage)+"','"+route+"','"+stop+"','"+reason+"','"+currentTimeStamp+"','"+currentTimeStamp+"')")
        connection.commit()

        RxMessage = "Scan Logged"

        # After scan is logged, write received and reset bit
        comm.Write("DockDoorScanner" + door + ".RxMessage", RxMessage)
        comm.Write("DockDoorScanner" + door + ".RxTriggerID", TxTriggerID)
        comm.Write("DockDoorScanner" + door + ".TxTrigger", False)
        print("Scan Logged")
        
        
    
        # Execute Scan Reason Logic
        
        noRead = scanPause.no_read(TxMessage, door)
        
        multiRead = scanPause.multi_read(TxMessage, door)
        
        codeNotFound = False        
        routeNotFound = False
        stopNotFound = False
        nextRoute = False
        wrongRoute = False
        lateContainer = False
        stopEarly = False
        newStopDockPicks = False
        newStopNoDockPicks = False
        
        if not noRead and not multiRead:
            
            codeNotFound = scanPause.code_not_found(TxMessage, door)
            
            if not codeNotFound:               
                
                routeNotFound = scanPause.route_not_found(TxMessage, door)
                
                stopNotFound = scanPause.stop_not_found(TxMessage, door)
                
                nextRoute = scanPause.next_route(TxMessage, door)
                
                wrongRoute = scanPause.wrong_route(TxMessage, door)
                
                lateContainer = scanPause.late_container(TxMessage, door)
                
                stopEarly = scanPause.stop_early(TxMessage, door)
                
                newStopDockPicks = scanPause.new_stop_dock_picks(TxMessage, door)
                
                newStopNoDockPicks = scanPause.new_stop_no_dock_picks(TxMessage, door)
                
            else:
                
                routeNotFound = False
                stopNotFound = False
                nextRoute = False
                wrongRoute = False
                lateContainer = False
                stopEarly = False
                newStopDockPicks = False
                newStopNoDockPicks = False
        else:
            codeNotFound = False
            
        
        print("No Read = " +str(noRead))
        print("Multi-Read = " +str(multiRead))
        print("No Code = " +str(codeNotFound))
        print("Route Not Found = " +str(routeNotFound))
        print("Stop Not Found = " +str(stopNotFound))
        print("Next Route = " +str(nextRoute))
        print("Wrong Route = " +str(wrongRoute))
        print("Late Container = " +str(lateContainer))
        print("Stop Early = " +str(stopEarly))
        print("New Stop Dock Picks = " +str(newStopDockPicks))
        print("New Stop No Dock Picks = " +str(newStopNoDockPicks))
        
        reason = ""
        
        if noRead or multiRead or codeNotFound or routeNotFound or stopNotFound or nextRoute or wrongRoute or lateContainer or stopEarly or newStopDockPicks or newStopNoDockPicks:
            
            comm.Write("wxsDoor" + str(door) + "Pause", True)
            pauseBit = "True"        
        
            reason = ""
            
            if noRead:
                reason = "No Read"
            elif multiRead:
                reason = "Multi-Read"
            elif codeNotFound:
                reason = "Code not Found"
            elif routeNotFound:
                reason = "Route Not Found"
            elif stopNotFound:
                reason = "Stop Not Found"
            elif nextRoute:
                reason = "Next Route"
            elif wrongRoute:
                reason = "Wrong Route"
            elif lateContainer:
                reason = "Late Container"
            elif stopEarly:
                reason = "Stop Early"
            elif newStopDockPicks:
                reason = "New Stop Dock Picks"
            elif newStopNoDockPicks:
                reason = "New Stop No Dock Picks"
        else:
            comm.Write("wxsDoor" + str(door) + "Pause", False)
            pauseBit = "False"
            
        print("pause bit = "+ pauseBit)
        if reason != "":
            print("pause bit is True becasue: " +reason)
        
        return "true and processed"
            
         
        
        
        

        
       


    else:
        return "ValueError: Out of Range"


def poll_ribbon_switch(door):
    with PLC() as comm:
        comm.IPAddress = plcIP
        ret = comm.Read("wxsDoor1RibbonSwitch", datatype=BOOL)
        switch = ret.Value
        
        if switch == True:
            id = "SELECT last_id FROM wcs.pop_up_id WHERE door_no=" +"'"+str(door)+"'"
            cursor.execute(id)
            result = cursor.fetchone()
            id = result[0]
            
            delete = modal.delete(id)
            
            if delete == "Done":
                comm.Write("wxsDoor1RibbonSwitch", False)
                
    





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
            
            print(dock_scan_control(door))
            
            print(poll_ribbon_switch(door))
                      
        print("")
        
        
    
    except Exception as e:
        print(e) 
        
        

        with PLC() as comm:
            comm.IPAddress = plcIP
            # After scan is logged, write received and reset bit
            comm.Write("DockDoorScanner" + str(door) + ".RxMessage", "NACK")            
            comm.Write("DockDoorScanner" + str(door) + ".TxTrigger", False)
            print("Processing Error")
            
    finally:
        
            
        connection.close()
   
    time.sleep(0.250)
    
    
    

atexit.register(connection.close())