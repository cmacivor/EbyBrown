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



def current_route(door):
    try:
        config = python_config.read_db_config()
        host = config.get('host')
        user = config.get('user')        
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
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)