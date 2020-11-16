"""
Author: Sadik
Changelog:
-- Version: 1.0
-- Initial Release

"""


import time
import requests
from datetime import datetime
import sys
import atexit
import Mysql_Connection

connection = Mysql_Connection.get()
cursor = connection.cursor()

def remaining_to_scan(route, date):
    
    sql = "SELECT id FROM assignment.dat_master WHERE route_no="+ str(route) +" AND date='"+ str(date) +"' AND count_flag = 1"
    cursor.execute(sql)
    stops = []
    eligable_counts = {}
    eligable_counts[route] = len(cursor.fetchall())

    sql = "SELECT stop_no, count(*) as `count` FROM dat_master WHERE route_no = 101 GROUP BY stop_no ORDER BY stop_no DESC"
    cursor.execute(sql)
    records = cursor.fetchall()

    for r in records:
        stops.append(int(r[0]))
        eligable_counts[int(r[0])] = r[1]

    return stops, eligable_counts