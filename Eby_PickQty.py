"""
Author: Robert J. Ward
Changelog:
-- Version: 1.0 Robert J. Ward
    --- Initial Release
-- Version: 1.1 Yogini Marathe 2020-11-12
    --- Updates with referece to Jira Ticket https://pendant.atlassian.net/browse/WEB-73.
    --- Changed the pick_qty query and subsequent UPDATE to wcs.route_statuses
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



        
    


def update_route_pick_qty():
    rows = "SELECT id FROM wcs.route_statuses"
    cursor.execute(rows)
    result = cursor.fetchall()
    rows = []
    for i in result:
        rows.append(i[0])
    # print(rows)

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

        ## get the quantities for each pick group type from the dat_master table
        pick_qty = "SELECT COUNT(*), pick_group FROM assignment.dat_master WHERE route_no =" + str(
            route) + " AND date =" + "'" + str(date) + "' group by pick_group"        
        cursor.execute(pick_qty)
        result = cursor.fetchall()
        #print(result)

        # declare the quantity placeholders
        freezerQty = 0
        coolerQty = 0
        dryQty = 0
        #iterate the resultSet to get individual pick group counts
        for oneResult in result:
            (qty, pickGroup) = oneResult
            if pickGroup is not None:
                pickGroup = str(pickGroup).lower()
                if pickGroup == "dry":
                    dryQty = qty
                elif pickGroup == "freezer":
                    freezerQty = qty
                elif pickGroup == "cooler":
                    coolerQty = qty

        # Update the quantities , if no quantities are found then those will be 0 initial value
        cursor.execute("UPDATE wcs.route_statuses SET pick_qty=" + str(dryQty) + ", freezer_container=" + str(
            freezerQty) + ", cooler_container=" + str(coolerQty) + " WHERE id=" + str(row) + ";")
        connection.commit()

    return "pick quantites updated for " + str(len(rows)) + " route(s)"



def update_verify_trailers_pick_qty():
    results = "SELECT route, date FROM wcs.verify_trailers WHERE route_complete=0"
    cursor.execute(results)
    results = cursor.fetchall()
    
       
    for idx, r in enumerate(results):
        # print(results[idx][0])
        # print(results[idx][1])
        
        ## get the quantities for each pick group type from the dat_master table
        pick_qty = "SELECT COUNT(*), pick_group FROM assignment.dat_master WHERE route_no =" + str(
            results[idx][0]) + " AND date =" + "'" + str(results[idx][1]) + "' group by pick_group"        
        cursor.execute(pick_qty)
        result = cursor.fetchall()
        #print(result)

        # declare the quantity placeholders
        freezerQty = 0
        coolerQty = 0
        dryQty = 0
        #iterate the resultSet to get individual pick group counts
        for oneResult in result:
            (qty, pickGroup) = oneResult
            if pickGroup is not None:
                pickGroup = str(pickGroup).lower()
                if pickGroup == "dry":
                    dryQty = qty
                elif pickGroup == "freezer":
                    freezerQty = qty
                elif pickGroup == "cooler":
                    coolerQty = qty

        # Update the quantities , if no quantities are found then those will be 0 initial value
        cursor.execute("UPDATE wcs.verify_trailers SET dry_container=" + str(dryQty) + ", freezer_container=" + str(
            freezerQty) + ", cooler_container=" + str(coolerQty) + " WHERE route=" + str(results[idx][0]) + ";")
        connection.commit()
        
        
        
    return "pick quantites updated for " + str(len(results)) + " trailer(s)"
    
    
def update_early_late(door):
      currentRoute = "SELECT number, date FROM wcs.dashboard_routes"+str(door)+" WHERE route_type='current'"
      cursor.execute(currentRoute)
      result = cursor.fetchall()      
      currentRoute = result[0][0]
      currentDate = result[0][1]
      #print(currentRoute)
      
      nextRoute = "SELECT number, date FROM wcs.dashboard_routes"+str(door)+" WHERE route_type='next'"
      cursor.execute(nextRoute)
      result = cursor.fetchall()      
      nextRoute = result[0][0]
      nextDate = result[0][1]
      #print(nextRoute) 
      
      currentEarly = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no="+"'"+str(currentRoute)+"' AND date="+"'"+str(currentDate)+"' AND early=1"
      cursor.execute(currentEarly)
      result = cursor.fetchone()      
      currentEarly = result[0]
      #print(currentEarly)
      
      currentLate = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no="+"'"+str(currentRoute)+"' AND date="+"'"+str(currentDate)+"' AND late=1"
      cursor.execute(currentLate)
      result = cursor.fetchone()
      currentLate = result[0]
      #print(currentLate)
      
      nextEarly = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no="+"'"+str(nextRoute)+"' AND date="+"'"+str(nextDate)+"' AND early=1"
      cursor.execute(nextEarly)
      result = cursor.fetchone()
      nextEarly = result[0]
      #print(nextEarly)
      
      nextLate = "SELECT COUNT(*) FROM assignment.dat_master WHERE route_no="+"'"+str(nextRoute)+"' AND date="+"'"+str(nextDate)+"' AND late=1"
      cursor.execute(nextLate)
      result = cursor.fetchone()
      nextLate = result[0]
      #print(nextLate)
      
      cursor.execute("UPDATE wcs.dashboard_routes"+str(door)+" SET early="+"'"+str(currentEarly)+"',late="+"'"+str(currentLate)+"' WHERE route_type='current';")
      cursor.execute("UPDATE wcs.dashboard_routes"+str(door)+" SET early="+"'"+str(nextEarly)+"',late="+"'"+str(nextLate)+"' WHERE route_type='next';")
      connection.commit()
      
      return "Door " + str(door) + ": Early/Late - has been updated"
      
      
    
    
doors = [1, 2]

while True:

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor()

        updatePickQty = update_route_pick_qty()
        print(updatePickQty)

        print(update_verify_trailers_pick_qty())
        
        for door in doors:
            print(update_early_late(door))


    except Exception as e:
        print(e)



    finally:
        connection.close()

    time.sleep(1)

atexit.register(connection.close())
