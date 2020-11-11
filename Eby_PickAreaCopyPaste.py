"""
Author: Sadikur Rahaman
Changelog:
-- Version: 1.0
-- Initial Release
"""

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
wcsdatabase = config.get('wcsdatabase')
database = config.get('database')
password = config.get('password')

def find_and_replace():
    # scan assignment.dat_master for null pick_area and pick_group fields
    try:
        connection = mysql.connector.connect(
                            host= host, 
                            user= user, 
                            database= database, 
                            password= password 
                        )
        # wcsconnection = mysql.connector.connect(
        #                     host= host, 
        #                     user= user, 
        #                     database= wcsdatabase, 
        #                     password= password 
        #                 )

        cursor = connection.cursor()
        #wcscursor = wcsconnection.cursor()

        sql = "SELECT pick_code FROM assignment.dat_master WHERE pick_area IS NULL OR pick_group IS NULL"
        cursor.execute(sql)
        result = cursor.fetchall()
        #print(result)
        
        counter = 0
        for item in result:
            if item[0] is not None:
                pickCode = item[0]
                #print(pickCode)
                sql = "SELECT `pick_area`, `group` FROM wcs.pick_areas WHERE code = "+"'"+ str(pickCode) + "'"
                cursor.execute(sql)
                result = cursor.fetchone()
                print(result)
                if result is not None and result[0] is not None:
                    print(result[0])
                    print(result[1])
                    sql = "UPDATE assignment.dat_master SET pick_area="+"'"+ result[0] + "', pick_group="+"'"+ result[1] + "' WHERE pick_code="+"'"+ item[0] + "'"
                    cursor.execute(sql)
                    connection.commit()
                    counter += 1
                    
        return "processed with " +str(counter) + " updates"

    except Exception as e:
        print(e)

    finally:
        cursor.close()
        connection.close()
        # wcscursor.close()
        # wcsconnection.close()





while True:
    function = find_and_replace()
    print(function)
    
    
    time.sleep(1)

