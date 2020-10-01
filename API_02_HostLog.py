"""
Author: Robert Ward

Version: 1.0

"""

"""
m_type must not be longer than 15 characters

"""

# Imports

import requests
import python_config
import mysql.connector
from datetime import datetime
import time

# Deployment Variables

api = "/api/hostlogs/store"


# Function


def log(auth, domain, source, m_type, message):
    dbLog(source, m_type, message)

    # loggingConfig = python_config.read_logging_config()
    # auth = loggingConfig.get('auth')
    # domain = loggingConfig.get('domain')
    # api = loggingConfig.get("api")
    # url = domain + api

    # parsedMessage = str(message).replace("b", "").replace("\\", "").replace("\x02", "").replace("\x03", "")

    # data = {"source": source, "type": m_type, "message": parsedMessage}

    # response = requests.post(url, json=data, allow_redirects=False)

    # test = response


def dbLog(source, m_typ, message):
    config = python_config.read_db_config()
    host = config.get('host')
    user = config.get('user')
    database = config.get('wcsdatabase')
    password = config.get('password')

    try:
        connection = mysql.connector.connect(
                host= host, 
                user= user, 
                database= database, 
                password= password 
            )

        cursor = connection.cursor()

        currentTimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        insertLogSql = ("INSERT INTO host_logs "
                                "(source, type, message, created_at, updated_at) "
                                "VALUES (%s, %s, %s, %s, %s)")
        
        parsedMessage = str(message).replace("b", "").replace("\\", "").replace("\x02", "").replace("\x03", "")
        
        newLog = (source, m_typ, parsedMessage, currentTimeStamp, currentTimeStamp)

        cursor.execute(insertLogSql, newLog)
        connection.commit()
    except Exception as e:
        print(e)


#test = log("Basic YWE6YQ==", "https://dev.pendantautomation.com", "WXS to Host", "Dock Scan Log Request", "Log Scan KD3101017-001")

#print(test)