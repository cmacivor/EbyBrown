

import mysql.connector
import schedule
import python_config
import Eby_Message
import time

#interval in seconds for processing messages
process_message_interval = 20

#get db credentials
config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('database')
wcsDatabase = config.get('wcsdatabase')
password = config.get('password')



def processMessages():
    print("processing messages from the host_logs table...")
    try:
        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= wcsDatabase, 
            password= password 
        )

        assignmentConnection = mysql.connector.connect(
            host = host,
            user = user,
            database = database,
            password = password
        )

        cursor = connection.cursor()
 
        sql = "select * from host_logs where type = 'UNKWN'"

        cursor.execute(sql)

        result = cursor.fetchall()
        for row in result:
            message = row[3]
            messageBase = Eby_Message.MessageBase(message)
            messageBase.getMessageType(assignmentConnection, row)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

#schedule.every(process_message_interval).seconds.do(run_threaded, processMessages)
schedule.every(process_message_interval).seconds.do(processMessages)


while 1:
    schedule.run_pending()
    time.sleep(1)
