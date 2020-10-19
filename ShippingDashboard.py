import mysql.connector
from mysql.connector import (connection)
import python_config
import GlobalFunctions
import sys
import traceback
import RouteStatus
import datetime

def updateDashboard():
    #get the highest priority non-completed Route Status of Door 1 
    unCompletedRouteStatus = getUnCompletedRouteStatuses()

    #update the dashboard_routes1 table with the route number and trailer number from highest priority row from the route_status table
    updateDashboardRoutes1(unCompletedRouteStatus.Route, unCompletedRouteStatus.TrailerNumber)

    #get rows from dat_master by the route number and date created
    datMasterRowsByRouteNoAndDate = getNumberRowsFromDatMasterByRouteNumberAndDate(unCompletedRouteStatus.Route, unCompletedRouteStatus.DateAt)

    #update the dashboard_routes table with the value
    updateDashboardRouteTotalExpected(datMasterRowsByRouteNoAndDate)

    calculateRemainingToScan()


def calculateRemainingToScan():
    currentDashboardRoute1 = getCurrentDashboardRoute1()
    total_expected = currentDashboardRoute1[2]
    door_scanned = currentDashboardRoute1[3]
    remaining_to_scan = total_expected - door_scanned
    updateRemainingToScan(remaining_to_scan)


def updateRemainingToScan(remaingToScan):
    try:
        config = python_config.read_db_config()
        host = config.get('host')
        user = config.get('user')
        #database = config.get('database')
        wcsDatabase = config.get('wcsdatabase')
        password = config.get('password')

        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= wcsDatabase, 
            password= password 
        )

        cursor = connection.cursor()

        currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql = "update wcs.dashboard_routes1 set remaining_to_scan = %s, updated_at = %s where route_type = 'current'"

        updateValues = (remaingToScan, currentTimeStamp)

        cursor.execute(sql, updateValues)

        connection.commit()

        cursor.close()

        connection.close()
    except Exception as e:
        print(e)


def getCurrentDashboardRoute1():
    try:
        config = python_config.read_db_config()
        host = config.get('host')
        user = config.get('user')
        #database = config.get('database')
        wcsDatabase = config.get('wcsdatabase')
        password = config.get('password')

        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= wcsDatabase, 
            password= password 
        )

        cursor = connection.cursor()

        sql = "select * from wcs.dashboard_routes1 where route_type = 'current'"

        cursor.execute(sql)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result
    except Exception as e:
        print(e)



def updateDashboardRouteTotalExpected(total):
    try:
        config = python_config.read_db_config()
        host = config.get('host')
        user = config.get('user')
        #database = config.get('database')
        wcsDatabase = config.get('wcsdatabase')
        password = config.get('password')

        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= wcsDatabase, 
            password= password 
        )

        cursor = connection.cursor()

        currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        sql = "update wcs.dashboard_routes set total_expected = %s, updated_at = %s where route_type = 'current'"

        updateValues = (total, currentTimeStamp)

        cursor.execute(sql, updateValues)

        connection.commit()

        cursor.close()

        connection.close()
    except Exception as e:
        print(e)

def getNumberRowsFromDatMasterByRouteNumberAndDate(routeNumber, routeStatusDate):
    try:
        config = python_config.read_db_config()
        host = config.get('host')
        user = config.get('user')
        #database = config.get('database')
        wcsDatabase = config.get('wcsdatabase')
        password = config.get('password')

        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= wcsDatabase, 
            password= password 
        )

        cursor = connection.cursor()

        sql = "select count(*) from assignment.dat_master where route_no = %s and DATE(created_at) = %s "

        selectValues = (routeNumber, routeStatusDate)

        cursor.execute(sql, selectValues)

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result[0]
    except Exception as e:
        print(e)
    


def updateDashboardRoutes1(routeNumber, trailerNumber):
    try:
        config = python_config.read_db_config()
        host = config.get('host')
        user = config.get('user')
        #database = config.get('database')
        wcsDatabase = config.get('wcsdatabase')
        password = config.get('password')

        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= wcsDatabase, 
            password= password 
        )

        currentTimeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor = connection.cursor()

        sql = "update wcs.dashboard_routes1 set number = %s, trailer = %s, updated_at = %s where route_type = 'current'"

        updateValues = (routeNumber, trailerNumber, currentTimeStamp)

        cursor.execute(sql, updateValues)

        connection.commit()

        rowCount = cursor.rowcount

        cursor.close()
        connection.close()

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()
    

def getUnCompletedRouteStatuses():
    try:
        config = python_config.read_db_config()
        host = config.get('host')
        user = config.get('user')
        #database = config.get('database')
        wcsDatabase = config.get('wcsdatabase')
        password = config.get('password')

        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= wcsDatabase, 
            password= password 
        )

        cursor = connection.cursor()

        getRouteStatusesSQL = "select * from route_statuses where status != 'Complete' order by priority limit 1"

        cursor.execute(getRouteStatusesSQL)

        #routeStatusObjList = []

        result = cursor.fetchone()

        #for routeStatus in result:
        routeStatusObj = RouteStatus.route_status(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], 
                                                        result[8], result[9], 0, 0)

        return routeStatusObj
            #routeStatusObjList.append(routeStatusObj)

        #return routeStatusObjList

    except Exception as e:
        print(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails) 




if __name__ == "__main__":
    updateDashboard()






