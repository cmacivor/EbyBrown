import GlobalFunctions
import sys
import traceback
import mysql.connector
import python_config

def process(containerId):
    #query the dat_master table against the containerId, get the jurisdiction and qty
    datFileRecord = getDatFileRecordByContainerId(containerId)

    #create the sub dat file

def getDatFileRecordByContainerId(containerId):
    try:
        config = python_config.read_db_config()
        host = config.get('host')
        user = config.get('user')
        database = config.get('database')
        password = config.get('password')

        assignmentConnection = mysql.connector.connect(
            host = host,
            user = user,
            database = database,
            password = password
        )

        cursor = assignmentConnection.cursor()
 
        sql = "select * from dat_master where container_id = %s"

        queryValues = (containerId,)

        cursor.execute(sql, queryValues)

        result = cursor.fetchone()

        cursor.close()
        assignmentConnection.close()
        return result
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)


if __name__ == "__main__":
    process("FB1005530-007  ")