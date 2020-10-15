import socket
from time import sleep
import mysql.connector
from mysql.connector import (connection)
import python_config
import Eby_GlobalConstants as GlobalConstants


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

# HOST = '10.22.56.11'  # The server's hostname or IP address
# PORT = 9998        # The port used by the server

def getLogs():
    try:
        config = python_config.read_db_config()
        host = config.get('host')
        user = config.get('user')
        database = config.get('database')
        #wcsDatabase = config.get('wcsdatabase')
        password = config.get('password')

        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= database, 
            password= password 
        )

        cursor = connection.cursor()

        SQL = "select * from host_logs where type = 'ASGNCOMP' || type = 'ORDRCOMP' || type = 'CONTCOMP' || type = 'ROUTCOMP' || type = 'ADDCONTA'"

        cursor.execute(SQL)

        result = cursor.fetchall()

        return result
    except Exception as e:
        print(e)

        


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    hostLogsArr = []
    hostLogs = getLogs()
    for log in hostLogs:
        message = log[3]
        concatMsg = GlobalConstants.StartTransmissionCharacter + message + GlobalConstants.EndTransmissionCharacter
        encodedMessage = concatMsg.encode('ascii')
        hostLogsArr.append(encodedMessage)

    s.connect((HOST, PORT))

    while True:
        for msg in hostLogsArr:
            
            #s.sendall(b'\x027|KEEPALIV\x03')
            s.sendall(msg)

            data = s.recv(1024)
            print(data)
            sleep(0.1)

  
    
    # #sleep(10)

    # s.sendall(b'\x027|KEEPALIV\x03')
    # data1 = s.recv(1024)
    # print(data1)

    # #sleep(10)

    # s.sendall(b'\x027|KEEPALIV\x03')
    # data2 = s.recv(1024)
    # print(data2)


#print('Received', repr(data))