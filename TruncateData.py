import mysql.connector 
from datetime import datetime
import time
import python_config

#get db credentials
config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('database')
wcsDatabase = config.get('wcsdatabase')
password = config.get('password')

def truncateHostLogs():
    print("truncating from the host_logs table...")
    try:
        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= wcsDatabase, 
            password= password 
        )

        cursor = connection.cursor(buffered=True)
        sql = "DELETE FROM wcs.host_logs WHERE updated_at < SUBDATE(CURDATE(), 14)"
        cursor.execute(sql)
        connection.commit()
        print("Successfully Trancted data")

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

def truncatePlcLogs():
    print("truncating from the plc_logs table...")
    try:
        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= wcsDatabase, 
            password= password 
        )

        cursor = connection.cursor(buffered=True)
        sql = "DELETE FROM wcs.plc_logs WHERE updated_at < SUBDATE(CURDATE(), 14)"
        cursor.execute(sql)
        connection.commit()
        print("Successfully Trancted data")

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

truncateHostLogs()
truncatePlcLogs()