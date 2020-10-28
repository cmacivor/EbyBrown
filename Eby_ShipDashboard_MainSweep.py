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
    try:
        #connection = mysql.connector.connect(
        #    host= host, 
        #    user= user, 
        #    database= wcsDatabase, 
        #    password= password 
        #)

        #cursor = connection.cursor()

        priority = "SELECT MIN(priority) FROM wcs.route_statuses WHERE status <> \"Complete\" AND dock_door = " + str(door)

        cursor.execute(priority)
        result = cursor.fetchone()
        priority = result[0]
        #print(priority)

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

        dry = "SELECT pick_qty FROM wcs.route_statuses WHERE priority = " + str(priority)
        cursor.execute(dry)
        result = cursor.fetchone()
        dry = result[0]
        #print(dry)

        date = "SELECT date FROM wcs.route_statuses WHERE priority = " + str(priority)
        cursor.execute(date)
        result = cursor.fetchone()
        date = result[0]
        #print(date)

        scanned = 40   

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET number=" + str(route) + " WHERE route_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET total_expected=" + str(dry) + " WHERE route_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET door_scanned=" + str(scanned) + " WHERE route_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET door_no_read=" + str(0) + " WHERE route_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET late=" + str(0) + " WHERE route_type = 'current';")
        #connection.commit()

        remaining_to_scan = dry - scanned
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET remaining_to_scan=" + str(remaining_to_scan) + " WHERE route_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET trailer=" + str(trailer_number) + " WHERE route_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET date=" + "'" + str(date) + "'" + " WHERE route_type = 'current';")
        #connection.commit()

        currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #print(currentTimeStamp)        
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET updated_at=" + "'" + currentTimeStamp + "'" + " WHERE route_type = 'current';")
        connection.commit()



        #cursor.close()
        #connection.close()

        return "success - Current Route Door " + str(door)


    except Exception as e:
        print(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)




def next_route(door):
    try:
        #connection = mysql.connector.connect(
        #    host= host, 
        #    user= user, 
        #    database= wcsDatabase, 
        #    password= password 
        #)

        #cursor = connection.cursor()

        priorities = "SELECT priority FROM wcs.route_statuses WHERE status <> \"Complete\" AND dock_door = " + str(door)

        cursor.execute(priorities)
        result = cursor.fetchall()
        #print(result)
        result_list = []
        for i in result:
            result_list.append(i[0])
        result_list = sorted(result_list)        
        #print(result_list)
        if len(result_list) > 1:
            priority = result_list[1]
        else:
            priority = 0
        #print(priority)

        
        if priority != 0:
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

            dry = "SELECT pick_qty FROM wcs.route_statuses WHERE priority = " + str(priority)
            cursor.execute(dry)
            result = cursor.fetchone()
            dry = result[0]
            #print(dry)

            date = "SELECT date FROM wcs.route_statuses WHERE priority = " + str(priority)
            cursor.execute(date)
            result = cursor.fetchone()
            date = result[0]
            #print(date)

            scanned = 0

        else:
            route = 0
            door = door
            trailer_number = 0
            freezer = 0
            cooler = 0
            dry = 0
            scanned = 0
            date = 0

           

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET number=" + str(route) + " WHERE route_type = 'next';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET total_expected=" + str(dry) + " WHERE route_type = 'next';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET door_scanned=" + str(scanned) + " WHERE route_type = 'next';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET door_no_read=" + str(0) + " WHERE route_type = 'next';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET late=" + str(0) + " WHERE route_type = 'next';")
        #connection.commit()

        remaining_to_scan = dry - scanned
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET remaining_to_scan=" + str(remaining_to_scan) + " WHERE route_type = 'next';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET trailer=" + str(trailer_number) + " WHERE route_type = 'next';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET date=" + "'" + str(date) + "'" + " WHERE route_type = 'next';")
        #connection.commit()

        currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #print(currentTimeStamp)        
        cursor.execute("UPDATE wcs.dashboard_routes" + str(door) + " SET updated_at=" + "'" + currentTimeStamp + "'" + " WHERE route_type = 'next';")
        connection.commit()



        #cursor.close()
        #connection.close()

        if priority == 0:
            return "None"
        else:
            return "success - Next Route Door " + str(door)


    except Exception as e:
        print(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)



def previous_stop(door):
    try:
        #connection = mysql.connector.connect(
        #    host= host, 
        #    user= user, 
        #    database= wcsDatabase, 
        #    password= password 
        #)

        #cursor = connection.cursor()

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

        door_scanned = dry_goods_expected

        door_no_read = "SELECT door_no_read FROM wcs.dashboard_stops" + str(door) + " WHERE stop_type = 'current'"
        cursor.execute(door_no_read)
        result = cursor.fetchone()
        door_no_read = result[0]
        #print(door_no_read)

        late = 0

        pending_heavy = 0

        remaining_to_scan = dry_goods_expected - door_scanned

        
        # Write to previous stop
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET number=" + str(stop) + " WHERE stop_type = 'previous';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET dry_goods_expected=" + str(dry_goods_expected) + " WHERE stop_type = 'previous';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET door_scanned=" + str(door_scanned) + " WHERE stop_type = 'previous';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET door_no_read=" + str(door_no_read) + " WHERE stop_type = 'previous';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET late=" + str(late) + " WHERE stop_type = 'previous';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET pending_heavy=" + str(pending_heavy) + " WHERE stop_type = 'previous';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET remaining_to_scan=" + str(remaining_to_scan) + " WHERE stop_type = 'previous';")
        #connection.commit()

        currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #print(currentTimeStamp)        
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET updated_at=" + "'" + currentTimeStamp + "'" + " WHERE stop_type = 'previous';")
        connection.commit()

        return "success - Previous Stop Door " + str(door)


    except Exception as e:
        print(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)



def current_stop(door):
    try:
        #connection = mysql.connector.connect(
        #    host= host, 
        #    user= user, 
        #    database= wcsDatabase, 
        #    password= password 
        #)

        #cursor = connection.cursor()


        


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

        currentStop = "SELECT number FROM wcs.dashboard_stops" + str(door) + " WHERE stop_type = 'current'"
        cursor.execute(currentStop)
        result = cursor.fetchone()
        currentStop = result[0]
        #print(currentStop)


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
            return "None - Current Stop Door " + str(door)

        # Find Active Stop and picks per stop
        activeStop = 0
        previousStop = ""        
        while activeStop == 0:
            for i in stopsList:                
                if activeStop == 0:
                    idList = "SELECT id FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "'" + " AND stop_no=" + str(i)
                    cursor.execute(idList)
                    result = cursor.fetchall()
                    resultList = []
                    for r in result:
                        resultList.append(r[0])                
                    for result in resultList:
                        stopCheck = "SELECT stop_scan FROM assignment.dat_master WHERE id=" + str(result)
                        cursor.execute(stopCheck)
                        results = cursor.fetchone()
                        stopCheck = int(results[0])
                        #print(stopCheck)
                        if stopCheck == 0:
                            activeStop = str(i)
                            #print(activeStop)
                            carton_qty = len(resultList)
                            if currentStop != activeStop:
                                previousStop = previous_stop(int(door))
                                #print(previousStop)                                
                            break                        
                        else:
                            continue
                else:
                    break
            #print(activeStop)
            #print(carton_qty)

        
        # Find picks scanned
        totalScanned = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no=" + str(route) + " AND date=" + "'" + str(date) + "'" + " AND stop_no=" + str(activeStop) + " AND stop_scan=1"
        cursor.execute(totalScanned)
        result = cursor.fetchone()
        totalScanned = result[0]
        #print(totalScanned)


        


        # Write to dashboard stops table
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET number=" + str(activeStop) + " WHERE stop_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET dry_goods_expected=" + str(carton_qty) + " WHERE stop_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET door_scanned=" + str(totalScanned) + " WHERE stop_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET door_no_read=" + str(0) + " WHERE stop_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET late=" + str(0) + " WHERE stop_type = 'current';")
        #connection.commit()

        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET pending_heavy=" + str(0) + " WHERE stop_type = 'current';")
        #connection.commit()

        remaining_to_scan = carton_qty - totalScanned
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET remaining_to_scan=" + str(remaining_to_scan) + " WHERE stop_type = 'current';")
        #connection.commit()

        currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #print(currentTimeStamp)        
        cursor.execute("UPDATE wcs.dashboard_stops" + str(door) + " SET updated_at=" + "'" + currentTimeStamp + "'" + " WHERE stop_type = 'current';")
        connection.commit()


        #cursor.close()
        #connection.close()


        return "success - Current Stop Door " + str(door)






    
    except Exception as e:
        print(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)





while True:

    try:
        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= wcsDatabase, 
            password= password 
        )

        cursor = connection.cursor()


        current_door1 = current_route(1)
        print(current_door1)
        current_door2 = current_route(2)
        print(current_door2)
        next_route1 = next_route(1)
        print(next_route1)
        next_route2 = next_route(2)
        print(next_route2)
        current_stop1 = current_stop(1)
        print(current_stop1)
        current_stop2 = current_stop(2)
        print(current_stop2)


    except Exception as e:
        print(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)


    time.sleep(1)


atexit.register(cursor.close)
atexit.register = connection.close()

    
