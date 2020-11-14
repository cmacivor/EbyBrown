import Mysql_Connection
import time
import atexit

connection = Mysql_Connection.get()
cursor = connection.cursor()

def change_status(id, status):
    sql = "UPDATE assignment.dat_master SET status = "+"'"+ status +"'"+" WHERE id="+str(id)
    cursor.execute(sql)
    connection.commit()


def update_assignment_status():
    sql = "SELECT c_comp, stop_scan, id FROM assignment.dat_master WHERE status <> 'Shipped' OR status IS NULL"
    cursor.execute(sql)
    result = cursor.fetchall()
    for item in result:
        if item[0] == 0 and item[1] == 0:
            change_status(item[2], 'Pending')
        elif item[0] == 1 and item[1] == 0:
            change_status(item[2], 'Pick Complete')
        elif item[0] == 1 and item[1] == 1:
            change_status(item[2], 'Shipped')
    return 'assignment status updated successfully.'
        
while True:
    print(update_assignment_status())
    time.sleep(1)
    
    
atexit.register(connection.close())