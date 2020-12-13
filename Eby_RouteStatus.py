import time
from datetime import datetime
import Mysql_Connection


def route_status():
    sql = "SELECT route, date, id, dock_door FROM wcs.route_statuses WHERE status <> 'Shipped'"
    wcs_cursor.execute(sql)
    result = wcs_cursor.fetchall()
    # print(result)
    for item in result:
        c_comp_detail = get_c_comp_detail(item[0], item[1])
        #print("c_comp = " +str(c_comp_detail))
        dashboard_map_detail = get_dashboard_map_detail(item[0], item[1])
        #print("stop_scan = " +str(dashboard_map_detail))

        if c_comp_detail['is_none_c_comp_one'] == True:
            update_status(item[2], "Not Started", item[0])
            print("Route "+str(item[0])+" is in Not Started")
        if c_comp_detail['is_all_c_comp_one'] == True and dashboard_map_detail['is_all_dashboard_map_zero'] == True:
            update_status(item[2], "Pick Complete", item[0])
            print("Route "+str(item[0])+" is in Pick Complete")
        elif c_comp_detail['is_any_c_comp_one'] == True and dashboard_map_detail['is_all_dashboard_map_zero'] == True:
            update_status(item[2], "Picking", item[0])
            print("Route "+str(item[0])+" is in Picking")
        if dashboard_map_detail['is_all_dashboard_map_one'] == True:
            update_status(item[2], "Shipped", item[0])
            print("Route "+str(item[0])+" is in Shipped")
            cursor.execute("UPDATE wcs.dashboard_routes" +
                           str(item[3]) + " SET door_no_read=0 WHERE route_type = 'current';")
            cursor.execute("UPDATE wcs.dashboard_stops" +
                           str(item[3]) + " SET door_no_read=0 WHERE stop_type = 'current';")
            cursor.execute("UPDATE wcs.dashboard_stops" +
                           str(item[3]) + " SET door_no_read=0 WHERE stop_type = 'previous';")
            connection.commit()
        if dashboard_map_detail['is_any_dashboard_map_one'] == True:
            update_status(item[2], "In Shipping", item[0])
            print("Route "+str(item[0])+" is in Shipping")

    return "processed"


def get_c_comp_detail(route, date):
    sql = "SELECT c_comp FROM assignment.dat_master WHERE route_no='" + \
        str(route) + "' AND date='" + str(date) + "'"
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
        'is_any_c_comp_one': True if count_one_values > 0 and total != count_one_values else False,
        'is_none_c_comp_one': True if count_one_values == 0 else False,
    }


def get_dashboard_map_detail(route, date):
    sql = "SELECT dashboard_map FROM assignment.dat_master WHERE route_no='" + \
        str(route) + "' AND date='" + str(date) + "'"
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
        'is_all_dashboard_map_zero': True if total == count_zero_values else False,
        'is_all_dashboard_map_one': True if total == count_one_values else False,
        'is_any_dashboard_map_one': True if count_one_values > 0 and total != count_one_values else False,
    }


def update_status(id, status, route):
    sql = "UPDATE wcs.route_statuses SET status = '" + \
        status + "' WHERE id="+str(id)
    sql2 = "UPDATE wcs.verify_trailers SET status= '" + \
        status + "' WHERE route=" + str(route)
    # print(sql)
    wcs_cursor.execute(sql)
    wcs_cursor.execute(sql2)
    wcs_connection.commit()


while True:

    try:

        connection = Mysql_Connection.get()
        cursor = connection.cursor()

        wcs_connection = Mysql_Connection.get('wcsDatabase')
        wcs_cursor = wcs_connection.cursor()

        print(route_status())

    except Exception as e:
        print(e)

    finally:

        connection.close()
        wcs_connection.close()

    time.sleep(1)
