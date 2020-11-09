"""
Author: Robert J. Ward
Changelog:
-- Version: 1.0 Robert J. Ward
    --- Initial Release

"""

# Imports

import requests
import time
import requests
import python_config
import mysql.connector
from datetime import datetime
import sys
import atexit
import os


config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('wcsdatabase')
password = config.get('password')



def find_and_replace():
    # find code and replace with text

    idList = "SELECT id FROM assignment.dat_master WHERE pick_area IS NULL"
    cursor.execute(idList)
    results = cursor.fetchall()
    idList = []
    for idx, r in enumerate(results):
        idList.append(results[idx][0])
    #print(idList)

    for i in idList:
        fullPickCode = "SELECT pick_area FROM assignment.dat_master WHERE id=" +"'"+ str(i) + "'"
        cursor.execute(fullPickCode)
        result = cursor.fetchone()
        fullPickCode = result[0]
        pickCode = fullPickCode[3:]
        #print(pickCode)

        pickArea = "SELECT pick_area FROM wcs.pick_areas WHERE code=" +"'"+ str(pickCode) + "'"
        cursor.execute(pickArea)
        result = cursor.fetchone()
        result = cursor.fetchone()
        if result is not None:
            pickArea = result[0]
            #print(pickArea)

            cursor.execute("UPDATE assignment.dat_master SET pick_area=" +"'"+str(pickArea)+"' WHERE id=" +"'"+str(i)+"'")
            connection.commit()

    return "success"




while True:

    try:
        connection = mysql.connector.connect(
                        host= host, 
                        user= user, 
                        database= database, 
                        password= password 
                    )

        cursor = connection.cursor()


        function = find_and_replace()
        print(function)

        

    except Exception as e:
        print(e)

    finally:
        connection.close()


    time.sleep(5)

    
atexit.register(connection.close())