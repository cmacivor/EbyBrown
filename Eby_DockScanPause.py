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
latch_time = "36000"


def no_read(code, door):
    # Barcode missing or otherwise unable to be read

    try:

        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor()

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='No Read'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        # print(enabled)

        if enabled == 1:
            if "no" in code.lower():
                id = modal.pop_up("<br><br><br><br>NO READ<br><br><br><br><br>",
                                  "#000000", " #ED971A", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
                return True
            else:
                return False
        else:
            if "no" in code.lower():
                id = modal.pop_up("<br><br><br><br>NO READ<br><br><br><br><br>",
                                  "#000000", " #ED971A", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
            return False

    except Exception as e:
        print(e)

    finally:
        connection.close()


def multi_read(code, door):
    # Two barcodes read at same time

    try:

        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor()

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Multi Read'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        # print(enabled)

        if enabled == 1:

            if "multi" in code.lower():
                id = modal.pop_up("<br><br><br><br>MULTI-READ<br><br><br><br><br>",
                                  "#000000", " #E67E22", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
                return True
            else:
                return False
        else:
            if "multi" in code.lower():
                id = modal.pop_up("<br><br><br><br>MULTI-READ<br><br><br><br><br>",
                                  "#000000", " #E67E22", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
                return False
            return False

    except Exception as e:
        print(e)

    finally:
        connection.close()


def code_not_found(code, door):
    # barcode scanned doesn't exist in database (has to be the approved barcode symbology, containing the dash in the correct spot, correct number of characters, etc.)

    try:

        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor()

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Barcode Not Found'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        # print(enabled)

        exists = "SELECT COUNT(*) FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(exists)
        result = cursor.fetchone()
        exists = result[0]
        # print(exists)

        if enabled == 1:

            if exists == 0:
                id = modal.pop_up("<br><br>BARCODE<br>NOT<br>FOUND<br><br><br>",
                                  "#000000", " #85C1E9", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()

                return True
            else:
                return False
        else:
            if exists == 0:
                id = modal.pop_up("<br><br>BARCODE<br>NOT<br>FOUND<br><br><br>",
                                  "#000000", " #85C1E9", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
            return False

    except Exception as e:
        print(e)

    finally:
        connection.close()


def route_not_found(code, door):
    # Label scanned belongs to a route not in the database for that day

    try:

        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor(buffered=True)

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Route Not Found'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        # print(enabled)

        route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = int(result[0])
        # print(route)

        scanDate = "SELECT date FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(scanDate)
        result = cursor.fetchone()
        scanDate = result[0]
        # print(scanDate)

        routeDate = "SELECT date FROM wcs.verify_trailers"
        cursor.execute(routeDate)
        result = cursor.fetchone()
        routeDate = result[0]
        # print(routeDate)

        activeRoutes = "SELECT route FROM wcs.verify_trailers WHERE door_id=" + \
            str(door)
        cursor.execute(activeRoutes)
        results = cursor.fetchall()
        activeRoutes = []
        for idx, r in enumerate(results):
            activeRoutes.append(int(results[idx][0]))
        # print(activeRoutes)

        if enabled == 1:

            if route not in activeRoutes or scanDate != routeDate:
                id = modal.pop_up("<br><br>ROUTE<br>NOT<br>FOUND<br><br><br>",
                                  "#F4D03F", " #21618C", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
                return True
            else:
                return False
        else:
            if route not in activeRoutes or scanDate != routeDate:
                id = modal.pop_up("<br><br>ROUTE<br>NOT<br>FOUND<br><br><br>",
                                  "#F4D03F", " #21618C", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
            return False

    except Exception as e:
        print(e)

    finally:
        connection.close()


def stop_not_found(code, door):
    # Stop on route is not found

    try:

        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor()

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Stop Not Found'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        # print(enabled)

        route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = result[0]
        # print(route)

        stop = "SELECT stop_no FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(stop)
        result = cursor.fetchone()
        stop = result[0]
        # print(stop)

        date = "SELECT date FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(date)
        result = cursor.fetchone()
        date = result[0]
        # print(date)

        availableStops = "SELECT stop_no FROM assignment.dat_master WHERE route_no=" + \
            "'"+str(route)+"' AND date=" + "'"+str(date)+"'"
        cursor.execute(availableStops)
        results = cursor.fetchall()
        # print(availableStops)
        availableStops = []
        for idx, r in enumerate(results):
            if results[idx][0] not in availableStops:
                availableStops.append(results[idx][0])
        # print(availableStops)

        if enabled == 1:

            if stop not in availableStops:
                id = modal.pop_up("<br><br>STOP<br>NOT<br>FOUND<br><br><br>",
                                  "#201281", " #C0392B", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
                return True
            else:
                return False

        else:
            if stop not in availableStops:
                id = modal.pop_up("<br><br>STOP<br>NOT<br>FOUND<br><br><br>",
                                  "#201281", " #C0392B", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
            return False

    except Exception as e:
        print(e)

    finally:
        connection.close()


def next_route(code, door):
    # First container of next route scanned

    try:

        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor()

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Next Route'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        # print(enabled)

        route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = int(result[0])
        #print("Scanned Route= "+str(route))

        currentRoute = "SELECT number FROM wcs.dashboard_routes" + \
            str(door)+" WHERE route_type='current'"
        cursor.execute(currentRoute)
        result = cursor.fetchone()
        currentRoute = int(result[0])
        #print("Current Route= "+str(currentRoute))

        trailer_pre_verify = "SELECT pre_verify FROM wcs.verify_trailers WHERE route=" + \
            "'"+str(route)+"'"
        cursor.execute(trailer_pre_verify)
        result = cursor.fetchone()
        trailer_pre_verify = int(result[0])
        #print("pre_verify= "+str(trailer_pre_verify))

        if enabled == 1:

            if route == currentRoute and trailer_pre_verify == 0:

                id = modal.pop_up("<br>NEXT<br>ROUTE<br>"+str(currentRoute) +
                                  "<br><br>", "#0781E6", " #F0F706", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
                return True

            else:
                return False
        else:
            if route == currentRoute and trailer_pre_verify == 0:
                id = modal.pop_up("<br>NEXT<br>ROUTE<br>"+str(currentRoute) +
                                  "<br><br>", "#0781E6", " #F0F706", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()

            return False

    except Exception as e:
        print(e)

    finally:
        connection.close()


def wrong_route(code, door):
    # Container scanned does not belong to the current route or next route

    try:

        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor()

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Wrong Route'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        # print(enabled)

        route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = int(result[0])
        # print(route)

        stop = "SELECT stop_no FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(stop)
        result = cursor.fetchone()
        stop = int(result[0])
        # print(stop)

        currentRoute = "SELECT number FROM wcs.dashboard_routes" + \
            str(door)+" WHERE route_type='current'"
        cursor.execute(currentRoute)
        result = cursor.fetchone()
        currentRoute = int(result[0])
        # print(currentRoute)

        currentStop = "SELECT number FROM wcs.dashboard_stops" + \
            str(door)+" WHERE stop_type='current'"
        cursor.execute(currentStop)
        result = cursor.fetchone()
        currentStop = int(result[0])
        # print(currentStop)

        nextRoute = "SELECT number FROM wcs.dashboard_routes" + \
            str(door)+" WHERE route_type='next'"
        cursor.execute(nextRoute)
        result = cursor.fetchone()
        nextRoute = int(result[0])
        # print(nextRoute)

        currentRoute_lastStop = "SELECT MIN(stop_no) FROM assignment.dat_master WHERE route_no="+"'"+str(
            currentRoute)+"'"
        cursor.execute(currentRoute_lastStop)
        result = cursor.fetchone()
        currentRoute_lastStop = int(result[0])
        # print(currentRoute_lastStop)

        if nextRoute != 0:

            nextRoute_firstStop = "SELECT MAX(stop_no) FROM assignment.dat_master WHERE route_no="+"'"+str(
                nextRoute)+"'"
            cursor.execute(nextRoute_firstStop)
            result = cursor.fetchone()
            nextRoute_firstStop = int(result[0])
            # print(nextRoute_firstStop)
        else:
            nextRoute_firstStop = 0

        if route != currentRoute and route != nextRoute:

            wrongRoute = True
        elif route == nextRoute and stop != nextRoute_firstStop:

            wrongRoute = True

        elif route == nextRoute and currentStop != currentRoute_lastStop:

            wrongRoute = True

        else:
            wrongRoute = False

        print("wrong route= " + str(wrongRoute))

        if enabled == 1:

            if wrongRoute == True:
                id = modal.pop_up("<br><br><br>WRONG<br>ROUTE<br><br><br><br>",
                                  "#DBFD04", " #954F27", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
                return True
            else:
                return False

        else:
            if wrongRoute == True:
                id = modal.pop_up("<br><br><br>WRONG<br>ROUTE<br><br><br><br>",
                                  "#DBFD04", " #954F27", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                connection.commit()
            return False

    except Exception as e:
        print(e)

    finally:
        connection.close()


def late_container(code, door):
    # Container belongs to route, but the stop it's for is already loaded

    try:

        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor()

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Late Container'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        # print(enabled)

        route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = int(result[0])
        # print(route)

        currentRoute = "SELECT number FROM wcs.dashboard_routes" + \
            str(door)+" WHERE route_type='current'"
        cursor.execute(currentRoute)
        result = cursor.fetchone()
        currentRoute = int(result[0])
        # print(currentRoute)

        stop = "SELECT stop_no FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(stop)
        result = cursor.fetchone()
        stop = int(result[0])
        # print(stop)

        currentStop = "SELECT number FROM wcs.dashboard_stops" + \
            str(door)+" WHERE stop_type='current'"
        cursor.execute(currentStop)
        result = cursor.fetchone()
        currentStop = int(result[0])
        # print(stop)

        if enabled == 1:

            if route == currentRoute and stop > currentStop:
                id = modal.pop_up("<br><br><br>LATE<br>CONT.<br><br><br><br>",
                                  "#000000", " #FE0800", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"';")
                cursor.execute(
                    "UPDATE assignment.dat_master SET late=1 WHERE container_id="+"'"+str(code)+"';")
                connection.commit()

                return True
            else:
                return False

        else:
            if route == currentRoute and stop > currentStop:
                id = modal.pop_up("<br><br><br>LATE<br>CONT.<br><br><br><br>",
                                  "#000000", " #FE0800", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"'")
                cursor.execute(
                    "UPDATE assignment.dat_master SET late=1 WHERE container_id="+"'"+str(code)+"';")
                connection.commit()

            return False

    except Exception as e:
        print(e)

    finally:
        connection.close()


def stop_early(code, door, next_stop):
    # Container for current route but for a later stop than is being loaded currently

    try:

        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor()

        enabled = "SELECT status FROM wcs.scan_reasons WHERE location='Shipping Dock' AND reason='Stop Early'"
        cursor.execute(enabled)
        result = cursor.fetchone()
        enabled = int(result[0])
        # print(enabled)

        route = "SELECT route_no FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(route)
        result = cursor.fetchone()
        route = int(result[0])
        # print(route)

        stop = "SELECT stop_no FROM assignment.dat_master WHERE container_id=" + \
            "'" + str(code) + "'"
        cursor.execute(stop)
        result = cursor.fetchone()
        stop = int(result[0])
        # print(stop)

        activeRoute = "SELECT number FROM wcs.dashboard_routes" + \
            str(door)+" WHERE route_type='current'"
        cursor.execute(activeRoute)
        result = cursor.fetchone()
        activeRoute = int(result[0])
        # print(activeRoute)

        activeStop = "SELECT number FROM wcs.dashboard_stops" + \
            str(door)+" WHERE stop_type='current'"
        cursor.execute(activeStop)
        result = cursor.fetchone()
        activeStop = int(result[0])
        # print(activeStop)

        if enabled == 1:

            if route == activeRoute and stop != next_stop and stop < activeStop:
                id = modal.pop_up("<br><br><br>STOP<br>EARLY<br><br><br><br>",
                                  "#000000", " #0096FE", latch_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"';")
                cursor.execute(
                    "UPDATE assignment.dat_master SET early=1 WHERE container_id="+"'"+str(code)+"';")
                connection.commit()

                return True
            else:
                return False

        else:
            if route == activeRoute and stop != next_stop and stop < activeStop:
                id = modal.pop_up("<br><br><br>STOP<br>EARLY<br><br><br><br>",
                                  "#000000", " #0096FE", display_time, str(door))
                cursor.execute("UPDATE wcs.pop_up_id SET last_id=" +
                               "'"+str(id)+"' WHERE door_no="+"'"+str(door)+"';")
                cursor.execute(
                    "UPDATE assignment.dat_master SET early=1 WHERE container_id="+"'"+str(code)+"';")
                connection.commit()
            return False

    except Exception as e:
        print(e)

    finally:
        connection.close()
