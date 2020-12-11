"""
Author: Robert J. Ward
Changelog:
-- Version: 1.0 Robert J. Ward
    --- Initial Release
-- Version: 1.1 Robert J. Ward
    --- Add dynamic Verify Trailers Priority mapping
-- Version: 1.2 Robert J. Ward
    --- Add dynamic Verify Trailers Trailers mapping

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
database = config.get('wcsdatabase')
password = config.get('password')





def add_routes(door):
    
    ids = "SELECT id FROM wcs.route_statuses WHERE dock_door=" + str(door) + " AND status<>'Complete'"
    cursor.execute(ids)
    result = cursor.fetchall()
    ids = []
    for i in result:
        ids.append(i[0])
    #print(ids)

    reviewed = 0
    copied = 0
    deleted = 0
    for record in ids:
        #print(record)
        reviewed += 1

        route = "SELECT route FROM wcs.route_statuses WHERE id=" + str(record)
        cursor.execute(route)
        result = cursor.fetchone()
        route = str(result[0])
        #print(route)

        trailer_number = "SELECT trailer_number FROM wcs.route_statuses WHERE id=" + str(record)
        cursor.execute(trailer_number)
        result = cursor.fetchone()
        trailer_number = str(result[0])
        #print(trailer_number)

        freezer_container = "SELECT freezer_container FROM wcs.route_statuses WHERE id=" + str(record)
        cursor.execute(freezer_container)
        result = cursor.fetchone()
        freezer_container = str(result[0])
        #print(freezer_container)

        cooler_container = "SELECT cooler_container FROM wcs.route_statuses WHERE id=" + str(record)
        cursor.execute(cooler_container)
        result = cursor.fetchone()
        cooler_container = str(result[0])
        #print(cooler_container)

        pick_qty = "SELECT pick_qty FROM wcs.route_statuses WHERE id=" + str(record)
        cursor.execute(pick_qty)
        result = cursor.fetchone()
        pick_qty = str(result[0])
        #print(pick_qty)

        priority = "SELECT priority FROM wcs.route_statuses WHERE id=" + str(record)
        cursor.execute(priority)
        result = cursor.fetchone()
        priority = str(result[0])
        #print(priority)

        status = "SELECT status FROM wcs.route_statuses WHERE id=" + str(record)
        cursor.execute(status)
        result = cursor.fetchone()
        status = str(result[0])
        #print(status)

        date = "SELECT date FROM wcs.route_statuses WHERE id=" + str(record)
        cursor.execute(date)
        result = cursor.fetchone()
        date = str(result[0])
        #print(date)

        

        # Check if Route already exists in table
        routes = "SELECT route FROM wcs.verify_trailers WHERE dock_door_number=" + str(door)
        cursor.execute(routes)
        results = cursor.fetchall()        
        routes = []
        for r in results:
            routes.append(r[0])        
        #print(routes)
        
        
        if str(route) not in routes:
            #print(route)
            copied += 1

            # Delete duplicate if exist
            cursor.execute("DELETE FROM wcs.verify_trailers WHERE route="+route+" AND date='"+date+"'")
            deleted += 1

            # Insert record to verify_trailers table
            cursor.execute("INSERT INTO wcs.verify_trailers (door_id,route,dock_door_number,trailer_number,freezer_container,cooler_container,dry_container,priority,status,date) VALUES ("+str(door)+","+route+","+str(door)+","+trailer_number+","+freezer_container+","+cooler_container+","+pick_qty+","+priority+","+"'"+status+"','"+date+"')")
            connection.commit()

        else:
            pass

    
    


    return str(reviewed) + " routes reviewed; " + str(copied) + " routes copied; " + str(deleted) + " routes deleted"
         


def freezer_cooler_picks():
    routes = "SELECT route FROM wcs.verify_trailers WHERE status<>'Shipped'"
    cursor.execute(routes)
    results = cursor.fetchall()
    routes = []
    for idx, r in enumerate(results):
        routes.append(results[idx][0])
    #print(routes)
    
    date = "SELECT date FROM wcs.verify_trailers WHERE route="+"'"+str(routes[0])+"'"
    cursor.execute(date)
    result = cursor.fetchone()
    date = result[0]
    #print(date)
    
    for r in routes:
        
        pickGroup = ["Freezer", "Cooler"]
        for p in pickGroup:
            count = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no="+"'"+str(r)+"' AND date="+"'"+str(date)+"' AND pick_group="+"'"+str(p)+"'"
            cursor.execute(count)
            result = cursor.fetchone()
            count = int(result[0])
            #print(count)
            
            if count > 0:
                count_scanned = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no="+"'"+str(r)+"' AND date="+"'"+str(date)+"' AND pick_group="+"'"+str(p)+"' AND stop_scan=1"
                cursor.execute(count_scanned)
                result = cursor.fetchone()
                count_scanned = int(result[0])
                #print(count_scanned)
                
                if count_scanned > 0:
                    cursor.execute("UPDATE wcs.verify_trailers SET "+str(p)+"=1 WHERE route="+"'"+str(r)+"'")
                    cursor.execute("UPDATE assignment.dat_master SET dashboard_map=1, stop_scan=1 WHERE route_no="+"'"+str(r)+"' AND date="+"'"+str(date)+"' AND pick_group="+"'"+str(p)+"'")
                    connection.commit()
                else:
                    pass
            else:
                pass
    
    return "freezer/cooler picks processed"
            
        
# v1.1, v1.2
def priority_update():

    currentRoutes = "SELECT route FROM wcs.verify_trailers"
    cursor.execute(currentRoutes)
    results = cursor.fetchall()
    currentRoutes = []
    for idx, r in enumerate(results):
        currentRoutes.append(results[idx][0])

    for route in currentRoutes:
        date = "SELECT date FROM wcs.verify_trailers WHERE route=" +"'"+str(route)+"'"
        cursor.execute(date)
        result = cursor.fetchone()
        date = result[0]

        priority = "SELECT priority FROM wcs.route_statuses WHERE route="+"'"+str(route)+"' AND date="+"'"+str(date)+"'"
        cursor.execute(priority)
        result = cursor.fetchone()
        priority = result[0]

        trailer = "SELECT trailer_number FROM wcs.route_statuses WHERE route="+"'"+str(route)+"' AND date="+"'"+str(date)+"'"
        cursor.execute(priority)
        result = cursor.fetchone()
        trailer = result[0]

        cursor.execute("UPDATE wcs.verify_trailers SET priority="+"'"+str(priority)+"',trailer_number="+"'"+str(trailer)+"' WHERE route="+"'"+str(route)+"'")

    connection.commit()

    return "priority/trailer update - complete"







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
            routes = add_routes(door)
            print(routes)
            
        print(freezer_cooler_picks())

        print(priority_update())
    
        

    except Exception as e:
        print(e)
        
        
        
    finally:
        
        connection.close()


    

    time.sleep(2)




atexit.register(connection.close())
