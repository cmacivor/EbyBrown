import mysql.connector
from mysql.connector import (connection)
import python_config
import GlobalFunctions
import sys
import traceback
import RouteStatus


def main():
    unCompletedRouteStatuses = getUnCompletedRouteStatuses()
    test = unCompletedRouteStatuses
    

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

        getRouteStatusesSQL = "select * from route_statuses where status != 'Complete' order by priority"

        cursor.execute(getRouteStatusesSQL)

        routeStatusObjList = []
        result = cursor.fetchall()
        for routeStatus in result:
            routeStatusObj = RouteStatus.route_status(routeStatus[0], routeStatus[1], routeStatus[2], routeStatus[3], routeStatus[4], routeStatus[5], routeStatus[6], routeStatus[7], 
                                                        routeStatus[8], routeStatus[9], 0, 0)
            routeStatusObjList.append(routeStatusObj)

        return routeStatusObjList

    except Exception as e:
        print(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails) 




if __name__ == "__main__":
    main()






