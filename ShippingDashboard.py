import mysql.connector
from mysql.connector import (connection)
import python_config
import GlobalFunctions
import sys
import traceback
import RouteStatus


def main():
    #get the highest priority non-completed Route Status of Door 1 
    unCompletedRouteStatuses = getUnCompletedRouteStatuses()
    updateDashboardRoutes1(unCompletedRouteStatuses.Route, unCompletedRouteStatuses.TrailerNumber)

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

        cursor = connection.cursor()

        sql = "update wcs.dashboard_routes1 set number = %s, trailer = %s where route_type = 'current'"

        updateValues = (routeNumber, trailerNumber)

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
    main()






