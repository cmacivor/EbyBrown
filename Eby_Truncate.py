import Mysql_Connection
import time

def get_truncate_query(table):
    return "DELETE FROM "+ table +" WHERE updated_at < SUBDATE(CURDATE(), 14)"

def truncate_host_logs():
    sql = get_truncate_query("wcs.host_logs")
    cursor.execute(sql)
    connection.commit()
    return "Successfully truncated data from wcs.host_logs"

def truncate_plc_logs():
    sql = get_truncate_query("wcs.plc_logs")
    cursor.execute(sql)
    connection.commit()
    return "Successfully truncated data from wcs.plc_logs"

def truncate_route_statuses():
    sql = get_truncate_query("wcs.route_statuses")
    cursor.execute(sql)
    connection.commit()
    return "Successfully truncated data from wcs.route_statuses"

def truncate_dat_master():
    sql = get_truncate_query("assignment.dat_master")
    assignment_cursor.execute(sql)
    assignment_connection.commit()
    return "Successfully truncated data from assignment.dat_master"

def truncate_scan_log():
    sql = get_truncate_query("scan_log")
    plc_cursor.execute(sql)
    plc_connection.commit()
    return "Successfully truncated data from plc.scan_log"

while True:
    connection = Mysql_Connection.get("wcsDatabase")
    cursor = connection.cursor()

    assignment_connection = Mysql_Connection.get("database")
    assignment_cursor = assignment_connection.cursor()

    plc_connection = Mysql_Connection.get("plcDatabase")
    plc_cursor = plc_connection.cursor()

    message = truncate_host_logs()
    print(message)

    message = truncate_plc_logs()
    print(message)

    message = truncate_route_statuses()
    print(message)

    message = truncate_dat_master()
    print(message)

    # message = truncate_scan_log()
    # print(message)
    
    time.sleep(5)