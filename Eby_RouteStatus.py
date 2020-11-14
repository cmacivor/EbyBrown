import time
from datetime import datetime
import Mysql_Connection


connection = Mysql_Connection.get()
cursor = connection.cursor()

wcs_connection = Mysql_Connection.get('wcsDatabase')
wcs_cursor = wcs_connection.cursor()

def route_status():
    sql = "SELECT route, date, id FROM wcs.route_statuses WHERE status <> 'Shipped'"
    wcs_cursor.execute(sql)
    result = wcs_cursor.fetchall()
    for item in result:
        c_comp_detail = get_c_comp_detail(item[0], item[1])
        stop_scan_detail = get_stop_scan_detail(item[0], item[1])

        if c_comp_detail['is_all_c_comp_one'] == True and stop_scan_detail['is_all_stop_scan_zero'] == True:
            update_status(item[2], "Pick Complete")
        elif c_comp_detail['is_any_c_comp_one'] == True and stop_scan_detail['is_all_stop_scan_zero'] == True:
            update_status(item[2], "Picking")
        if stop_scan_detail['is_all_stop_scan_one'] == True:
            update_status(item[2], "Shipped")
        if stop_scan_detail['is_any_stop_scan_one'] == True:
            update_status(item[2], "In Shipping")

        return "processed"

def get_c_comp_detail(route, date):
    sql = "SELECT c_comp FROM assignment.dat_master WHERE route_no='"+ str(route) +"' AND date='"+ str(date) +"'"
    cursor.execute(sql)
    result = cursor.fetchall()
    total = len(result)
    one_values = [
        item
        for item in result if item[0] == 1
    ]
    count_one_values = len(one_values)
    return {
        'is_all_c_comp_one': True if total == count_one_values else False,
        'is_any_c_comp_one': True if count_one_values > 0 else False,
    }

def get_stop_scan_detail(route, date):
    sql = "SELECT stop_scan FROM assignment.dat_master WHERE route_no='"+ str(route) +"' AND date='"+ str(date) +"'"
    cursor.execute(sql)
    result = cursor.fetchall()
    total = len(result)
    zero_values = [
        item
        for item in result if item[0] == 0
    ]
    one_values = [
        item
        for item in result if item[0] == 1
    ]
    count_zero_values = len(zero_values)
    count_one_values = len(one_values)
    return {
        'is_all_stop_scan_zero': True if total == count_zero_values else False,
        'is_all_stop_scan_one': True if total == count_one_values else False,
        'is_any_stop_scan_one': True if count_one_values > 0 else False,
    }

def update_status(id, status):
    sql = "UPDATE wcs.route_statuses SET status = '"+ status +"' WHERE id="+str(id)
    wcs_cursor.execute(sql)
    wcs_connection.commit()


while(True):
    print(route_status())

    time.sleep(1)