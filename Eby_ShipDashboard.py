"""
Author: Robert J. Ward
Changelog:
-- Version: 1.0 Robert J. Ward
    --- Initial Release

"""

import mysql.connector
from mysql.connector import (connection)
import python_config
import GlobalFunctions
import sys
import traceback
import RouteStatus
import datetime
import schedule
import time
import atexit



config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')        
wcsDatabase = config.get('wcsdatabase')
password = config.get('password')







def current_route(door):
    

    priority = "SELECT MIN(priority) FROM wcs.route_statuses WHERE status <> \"Shipped\" AND dock_door = " + str(door)
    cursor.execute(priority)
    result = cursor.fetchone()
    priority = result[0]
    #print("This is door " + str(door) + " " + str(priority))
    
    if priority is None:
        
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET number=0,total_expected=0,door_scanned=0,"+
                       "door_no_read=0,early=0,late=0,remaining_to_scan=0,trailer=0,date='0000-00-00' WHERE route_type = 'current';")
        connection.commit()
        
        return "No Current Route for Door " + str(door)

    route = "SELECT route FROM wcs.route_statuses WHERE priority = " + str(priority)
    cursor.execute(route)
    result = cursor.fetchone()
    route = result[0]
    #print(route)

    date = "SELECT date FROM wcs.route_statuses WHERE priority = " + str(priority)
    cursor.execute(date)
    result = cursor.fetchone()
    date = result[0]
    #print(date)

    door = door

    trailer_number = "SELECT trailer_number FROM wcs.route_statuses WHERE priority = " + str(priority)
    cursor.execute(trailer_number)
    result = cursor.fetchone()
    trailer_number = result[0]
    #print(trailer_number)    

    dry = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND pick_group='Dry'"
    cursor.execute(dry)
    result = cursor.fetchone()
    dry = result[0]
    #print(dry)
    
    toBeScanned = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND count_flag=1"
    cursor.execute(toBeScanned)
    result = cursor.fetchone()
    toBeScanned = result[0]
    #print(toBeScanned)

    scanned = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND stop_scan=1 AND count_flag=1"
    cursor.execute(scanned)
    result = cursor.fetchone()
    scanned = result[0]
    #print(scanned)
    
    early = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND early=1"
    cursor.execute(early)
    result = cursor.fetchone()
    early = result[0]
    #print(early)
    
    late = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND late=1"
    cursor.execute(late)
    result = cursor.fetchone()
    late = result[0]
    #print(late)
    

        

    cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET number=" + str(route) + " WHERE route_type = 'current';")
    cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET total_expected=" + str(dry) + " WHERE route_type = 'current';")
    cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET door_scanned=" + str(scanned) + " WHERE route_type = 'current';")
    cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET early=" + str(early) + " WHERE route_type = 'current';")
    cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET late=" + str(late) + " WHERE route_type = 'current';")
    remaining_to_scan = toBeScanned - scanned
    cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET remaining_to_scan=" + str(remaining_to_scan) + " WHERE route_type = 'current';")
    cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET trailer=" + str(trailer_number) + " WHERE route_type = 'current';")
    cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET date=" + "'" + str(date) + "'" + " WHERE route_type = 'current';")
    currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET updated_at=" + "'" + currentTimeStamp + "'" + " WHERE route_type = 'current';")
    connection.commit()



    

    return "processed - Current Route Door " + str(door)

    




def next_route(door):
    

    priorities = "SELECT priority FROM wcs.route_statuses WHERE status <> \"Shipped\" AND dock_door = " + str(door)
    cursor.execute(priorities)
    result = cursor.fetchall()
    #print(result)
    
    no_next_route = False
    if result is None:
        no_next_route = True        
    result_list = []
    for i in result:
        result_list.append(i[0])
    result_list = sorted(result_list)        
    #print(result_list)
    
    if len(result_list) > 1:
        priority = result_list[1]
    else:
        no_next_route = True
        
    #print(priority)

    
    # if a Next Route exists
    if no_next_route ==  False:
        route = "SELECT route FROM wcs.route_statuses WHERE priority = " + str(priority)
        cursor.execute(route)
        result = cursor.fetchone()
        route = result[0]
        #print(route)

        door = door

        trailer_number = "SELECT trailer_number FROM wcs.route_statuses WHERE priority = " + str(priority)
        cursor.execute(trailer_number)
        result = cursor.fetchone()
        trailer_number = result[0]
        #print(trailer_number)

        date = "SELECT date FROM wcs.route_statuses WHERE priority = " + str(priority)
        cursor.execute(date)
        result = cursor.fetchone()
        date = result[0]
        #print(date)

        freezer = "SELECT freezer_container FROM wcs.route_statuses WHERE priority = " + str(priority)
        cursor.execute(freezer)
        result = cursor.fetchone()
        freezer = result[0]
        #print(freezer)

        cooler = "SELECT cooler_container FROM wcs.route_statuses WHERE priority = " + str(priority)
        cursor.execute(cooler)
        result = cursor.fetchone()
        cooler = result[0]
        #print(cooler)

        dry = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND pick_group='Dry'"
        cursor.execute(dry)
        result = cursor.fetchone()
        dry = result[0]
        #print(dry)
        
        toBeScanned = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND count_flag=1"
        cursor.execute(toBeScanned)
        result = cursor.fetchone()
        toBeScanned = result[0]
        #print(toBeScanned)

        scanned = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND stop_scan=1 AND count_flag=1"
        cursor.execute(scanned)
        result = cursor.fetchone()
        scanned = result[0]
        #print(scanned)
        
        early = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND early=1"
        cursor.execute(early)
        result = cursor.fetchone()
        early = result[0]
        #print(early)
        
        late = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND late=1"
        cursor.execute(late)
        result = cursor.fetchone()
        late = result[0]
        #print(late)    

    

        

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET number=" + str(route) + " WHERE route_type = 'next';")
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET total_expected=" + str(dry) + " WHERE route_type = 'next';")
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET early=" + str(early) + " WHERE route_type = 'next';")
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET late=" + str(late) + " WHERE route_type = 'next';")
        remaining_to_scan = toBeScanned - scanned
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET remaining_to_scan=" + str(remaining_to_scan) + " WHERE route_type = 'next';")
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET trailer=" + str(trailer_number) + " WHERE route_type = 'next';")
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET date=" + "'" + str(date) + "'" + " WHERE route_type = 'next';")
        currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET updated_at=" + "'" + currentTimeStamp + "'" + " WHERE route_type = 'next';")
        connection.commit()
        
        return "processed - Next Route Door " + str(door)
    
    
    # else if no Next Route exists
    elif no_next_route:

        ## Clear Next Route if No Next Route
        
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET number=0,total_expected=0,door_scanned=0,"+
                       "door_no_read=0,early=0,late=0,remaining_to_scan=0,trailer=0,date='0000-00-00' WHERE route_type = 'next';")
        connection.commit()
        
        return "No Next Route for Door " + str(door)
        
    else:
        return "Awwwww Snap " + str(door)


    

    


    



def previous_stop(door):
    

    stop = "SELECT number FROM wcs.dashboard_stops" + str(door) + " WHERE stop_type = 'current'"
    cursor.execute(stop)
    result = cursor.fetchone()
    stop = result[0]
    #print(stop)

    dry_goods_expected = "SELECT dry_goods_expected FROM wcs.dashboard_stops" + str(door) + " WHERE stop_type = 'current'"
    cursor.execute(dry_goods_expected)
    result = cursor.fetchone()
    dry_goods_expected = result[0]
    #print(dry_goods_expected)

    door_scanned = "SELECT door_scanned FROM wcs.dashboard_stops" + str(door) + " WHERE stop_type = 'current'"
    cursor.execute(door_scanned)
    result = cursor.fetchone()
    door_scanned = result[0]
    #print(door_scanned)

    door_no_read = "SELECT door_no_read FROM wcs.dashboard_stops" + str(door) + " WHERE stop_type = 'current'"
    cursor.execute(door_no_read)
    result = cursor.fetchone()
    door_no_read = result[0]
    #print(door_no_read)

    late = 0

    pending_heavy = 0
    
    remaining_to_scan = "SELECT remaining_to_scan FROM wcs.dashboard_stops" + str(door) + " WHERE stop_type = 'current'"
    cursor.execute(remaining_to_scan)
    result = cursor.fetchone()
    remaining_to_scan = result[0]
    #print(remaining_to_scan)
    

    
    # Write to previous stop
    cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET number=" + str(stop) + " WHERE stop_type = 'previous';")
    cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET dry_goods_expected=" + str(dry_goods_expected) + " WHERE stop_type = 'previous';")
    cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET door_scanned=" + str(door_scanned) + " WHERE stop_type = 'previous';")
    cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET door_no_read=" + str(door_no_read) + " WHERE stop_type = 'previous';")
    cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET late=" + str(late) + " WHERE stop_type = 'previous';")
    cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET pending_heavy=" + str(pending_heavy) + " WHERE stop_type = 'previous';")
    cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET remaining_to_scan=" + str(remaining_to_scan) + " WHERE stop_type = 'previous';")
    currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET updated_at=" + "'" + currentTimeStamp + "'" + " WHERE stop_type = 'previous';")
    connection.commit()

    return "processed - Previous Stop Door " + str(door)


    



def current_stop(door):
    
    route = "SELECT number FROM wcs.dashboard_routes" + str(door) + " WHERE route_type = 'current'"
    cursor.execute(route)
    result = cursor.fetchone()
    route = result[0]
    #print(route)

    date = "SELECT date FROM wcs.dashboard_routes" + str(door) + " WHERE route_type = 'current'"
    cursor.execute(date)
    result = cursor.fetchone()
    date = result[0]
    #print(date)

    activeStop = "SELECT number FROM wcs.dashboard_stops" + str(door) + " WHERE stop_type = 'current'"
    cursor.execute(activeStop)
    result = cursor.fetchone()
    activeStop = result[0]
    #print(activeStop)
    
    


    allStops = "SELECT stop_no FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "'"
    cursor.execute(allStops)
    result = cursor.fetchall()
    resultList = []
    stopsList = []
    for i in result:
        if int(i[0]) not in resultList:
            resultList.append(int(i[0]))
            stopsList = sorted(resultList, reverse=True)
    #print(stopsList)
    
    
    if len(stopsList) == 0:
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET number=0,dry_goods_expected=0,door_scanned=0,door_no_read=0,"+
                       "late=0,pending_heavy=0,remaining_to_scan=0 WHERE stop_type = 'current';")
        connection.commit()
        return "No Current Stop for Door " + str(door)
    
    currentStop = 0
    currentStop_index = 0
    
    if len(stopsList) > 0:
        for stop in stopsList:
            sql = "SELECT dashboard_map FROM assignment.dat_master WHERE route_no="+"'"+ str(route) +"' AND date='"+ str(date) +"' AND stop_no="+"'"+str(stop)+"'"
            cursor.execute(sql)
            result = cursor.fetchall()
            total = len(result)
            
            zero_values = [item for item in result if item[0] == 0]
            one_values = [item for item in result if item[0] == 1]
            
            count_zero_values = len(zero_values)
            count_one_values = len(one_values)
            
            if count_one_values != total:
                currentStop = stop
                currentStop_index = stopsList.index(stop)
                break
            else:
                continue
            
        
    if currentStop == 0:
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET number=0,dry_goods_expected=0,door_scanned=0,door_no_read=0,"+
                       "late=0,pending_heavy=0,remaining_to_scan=0 WHERE stop_type = 'current';")
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET number=0,dry_goods_expected=0,door_scanned=0,door_no_read=0,"+
                       "late=0,pending_heavy=0,remaining_to_scan=0 WHERE stop_type = 'previous';")
        connection.commit()
        return "No Current Stop (Due to dashboard_map being True) for Door " + str(door)
    
    else:   

        ## if stop availble    
        
        dry = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND stop_no="+"'"+str(currentStop)+"' AND pick_group='Dry'"
        cursor.execute(dry)
        result = cursor.fetchone()
        dry = result[0]
        #print(dry)
        
        toBeScanned = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND stop_no="+"'"+str(currentStop)+"' AND count_flag=1"
        cursor.execute(toBeScanned)
        result = cursor.fetchone()
        toBeScanned = result[0]
        #print(toBeScanned)
        
        # Find picks scanned
        totalScanned = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "'" + " AND stop_no=" + str(currentStop) + " AND stop_scan=1 AND count_flag=1"
        cursor.execute(totalScanned)
        result = cursor.fetchone()
        totalScanned = result[0]
        #print(totalScanned)

        if currentStop != activeStop:
            # copy No Reads from current stop to previous stop before writing over
            currentStop_noReads = "SELECT door_no_read FROM wcs.dashboard_stops" + str(door) + " WHERE stop_type='current'"
            cursor.execute(currentStop_noReads)
            result = cursor.fetchone()
            currentStop_noReads = result[0]
            #print(currentStop_noReads)
            
            cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET door_no_read=" + str(currentStop_noReads) + " WHERE stop_type = 'previous';")
            cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET door_no_read=0 WHERE stop_type = 'current';")
            connection.commit()
        else:
            pass
        


        # Write to dashboard stops table
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET number=" + str(currentStop) + " WHERE stop_type = 'current';")
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET dry_goods_expected=" + str(dry) + " WHERE stop_type = 'current';")
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET door_scanned=" + str(totalScanned) + " WHERE stop_type = 'current';")
        remaining_to_scan = toBeScanned - totalScanned
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET remaining_to_scan=" + str(remaining_to_scan) + " WHERE stop_type = 'current';")
        currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET updated_at=" + "'" + currentTimeStamp + "'" + " WHERE stop_type = 'current';")
        connection.commit()


        ## Execute Previous Stop
        
        if currentStop_index == 0:
            cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET number=0,dry_goods_expected=0,door_scanned=0,door_no_read=0,"+
                       "late=0,pending_heavy=0,remaining_to_scan=0 WHERE stop_type = 'previous';")
            connection.commit()
            
        else:
            previousStop_index = currentStop_index - 1
             
            previousStop = stopsList[previousStop_index]
             
            previous_dry = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND stop_no="+"'"+str(previousStop)+"' AND pick_group='Dry'"
            cursor.execute(previous_dry)
            result = cursor.fetchone()
            previous_dry = result[0]
            #print(previous_dry)
            
            previous_toBeScanned = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "' AND stop_no="+"'"+str(previousStop)+"' AND count_flag=1"
            cursor.execute(previous_toBeScanned)
            result = cursor.fetchone()
            previous_toBeScanned = result[0]
            #print(previous_toBeScanned)
            
            # Find picks scanned
            previous_totalScanned = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "'" + " AND stop_no=" + str(previousStop) + " AND stop_scan=1 AND count_flag=1"
            cursor.execute(previous_totalScanned)
            result = cursor.fetchone()
            previous_totalScanned = result[0]
            #print(previous_totalScanned)
            
            
            ## Write to table
            
            cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET number=" + str(previousStop) + " WHERE stop_type = 'previous';")
            cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET dry_goods_expected=" + str(previous_dry) + " WHERE stop_type = 'previous';")
            cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET door_scanned=" + str(previous_totalScanned) + " WHERE stop_type = 'previous';")
            previous_remaining_to_scan = previous_toBeScanned - previous_totalScanned
            cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET remaining_to_scan=" + str(previous_remaining_to_scan) + " WHERE stop_type = 'previous';")
            connection.commit()

        return "processed - Current Stop Door " + str(door)






doors = [1, 2]


while True:

    try:
        connection = mysql.connector.connect(
                host= host, 
                user= user, 
                database= wcsDatabase, 
                password= password 
            )

        cursor = connection.cursor()

        
        for door in doors:
            current_routes = current_route(door)
            print(current_routes)
            
            next_routes = next_route(door)
            print(next_routes)
            
            current_stops = current_stop(door)
            print(current_stops)
            
            # previous_stop is called within current_stop

       
    
        
    except Exception as e:
        print(e)
        
        
        
    finally:
        
        connection.close()


    time.sleep(1)



atexit.register = connection.close()

    
