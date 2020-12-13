"""
Author: Robert J. Ward
Changelog:
-- Version: 1.0 Robert J. Ward
    --- Initial Release

"""


import time
import requests
import python_config
import mysql.connector
from datetime import datetime
import sys
import atexit
import Mysql_Connection


config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('wcsdatabase')
password = config.get('password')

logging = python_config.read_logging_config()
auth = logging.get('auth')
domain = logging.get('domain')
plcIP = "10.22.56.34"


def count_flag():

    records = "SELECT id FROM assignment.dat_master WHERE status='Pending' AND count_flag <> 1"
    cursor.execute(records)
    records = cursor.fetchall()

    for r in records:
        pick_code = "SELECT pick_code FROM assignment.dat_master WHERE id=" + \
            "'" + str(r[0]) + "'"
        cursor.execute(pick_code)
        pick_code = cursor.fetchone()[0]
        print(pick_code)

        flag = "SELECT count_flag FROM wcs.pick_areas WHERE code=" + \
            "'" + str(pick_code) + "'"
        cursor.execute(flag)
        flag = cursor.fetchone()[0]
        print(flag)
        flag = str(flag)

        if flag == "1":
            cursor.execute(
                "UPDATE assignment.dat_master SET count_flag=1 WHERE id=" + str(r[0])+";")

    connection.commit()


while True:

    try:

        connection = Mysql_Connection.get()

        cursor = connection.cursor()

        print(count_flag())

    except Exception as e:
        print(e)

    finally:

        connection.close()

    time.sleep(2)


atexit.register(connection.close())
