
'''
Pendant Automation
Contact:(410) 939-7707
@author: Jeremy Scheuerman
@version: 2.5
Created:8/11/20
Last Updated:8/14/20
Changes:Resolved all issues, removed temp variables from header
Issues:All issues resolved
'''


# /home/jeremy/Documents/Pendant_automation/Lucas_Docs
import os, sys
# get get os stuff and file mod functions
import mysql.connector
from mysql.connector import (connection)
# get mysql stuff
import time
import schedule
# import for timer stuff
import atexit
# write code that happens if the script is terminated
import shutil
import python_config
from pathlib import Path, PureWindowsPath
from datetime import datetime
import API_02_HostLog as hostLog

#get db credentials
config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('database')
password = config.get('password')

#get logging parameters
loggingConfig = python_config.read_logging_config()
enabled = loggingConfig.get('enabled')
auth = loggingConfig.get('auth')
domain = loggingConfig.get('domain')


#get file paths
datFileConverterConfig = python_config.read_fileconverter_config()
inputPath = datFileConverterConfig.get('input_path')
outputPath = datFileConverterConfig.get('output_path')
inputProcessedPath = datFileConverterConfig.get('input_processed_path')
outputProcessedPath = datFileConverterConfig.get('output_processed_path')
fileDeleteInterval = datFileConverterConfig.get('file_delete_interval')

#TODO put these file paths into the config.ini
# deployment variables
input_path = PureWindowsPath(inputPath).__str__()
                     
# assign path of folder where the dat files are supposed to be
output_path = PureWindowsPath(outputPath).__str__()
# assign path to save output with dat files folder
input_processed_path = PureWindowsPath(inputProcessedPath).__str__()
# assign path for Processed .DAT files
output_processed_path = PureWindowsPath(outputProcessedPath).__str__()
check_interval = 5  # seconds
# amount of time to wait in between next check IN SECONDS
delete_interval = 24  # hours
# amount of time it waits to check for old records IN HOURS
deploy_db = "assignment"

# database file located dat_converter/database file
db_host = host #'10.22.56.11'
db_user = user #'wcs'
db_pass = password #'38qa_r4UUaW2d'
# insert database infromation

cnct = connection.MySQLConnection(user=db_user, password=db_pass, host=db_host)                                                        
# establish connection names
print("Connected to database succesfully")
mycursor = cnct.cursor()
# get cursor
mycursor.execute("CREATE DATABASE IF NOT EXISTS " + deploy_db)
# create if it isnt there
mycursor.execute("USE " + deploy_db + ";")
# switch to right database

class route_status:
    def __init__(self, id, route, dockDoor, trailerNumber, priority, enable, status, date_at, created_at, updated_at, numberLines):
        self.ID = id
        self.Route = route
        self.DockDoor = dockDoor
        self.TrailerNumber = trailerNumber
        self.Priority = priority + numberLines
        self.Enable = enable
        self.Status = status
        self.DateAt = date_at
        self.CreatedAt = created_at
        self.UpdatedAt = updated_at
    



class obj_dat:
    # create object for easier organization and database management
    # here are the fieldstable_name for the mysql table
    line_dump = ""
    # place holder for line dump dat
    rec_id = "        "
    # record identifier
    # max length 8
    container_id = "               "
    # specific container for this pick 
    # max length 15
    assign_id = "                         "
    # assignment id for container
    # max length 25
    route_num = "      "
    # route number
    # max length 6
    stop_num = "    "
    # stop number
    # max length 4    
    pick_area = "      "
    # concotatenation of 3 digit stype and 3 digit pick area 
    # max length of 6
    pick_type = "          "
    # for full cas a description will be sent if no description it will just say full case
    # for split case it will always say split case
    # max length of 10
    juris = "      "
    # neede for cig stamping, if not cigs then its spaces, 
    # max length of 6
    carton_num = "  "
    # number of cigs in container, if not , spaces
    # max length 2
    c_comp = "0"
    # Container Complete 0=>No 1=>Yes
    a_comp = "0"
    # Assignment Complete 0=>No 1=>Yes
    o_comp = "0"
    # Order Complete 0=>No 1=>Yes
    r_comp = "0"
    # Route Complete 0=>No 1=>Yes
    assign_name = ""
    # Assignment Name from .dat file less the word "Assignment"
    status = ""
    # Not sure what this is here for
    priority = 0


def dat_table_create(table_name):
    # define cursor
    mytable = "CREATE TABLE IF NOT EXISTS " + table_name + """
    (id BIGINT(20) NOT NULL AUTO_INCREMENT , record_id VARCHAR(8) NOT NULL,
    container_id VARCHAR(15),assignment_id VARCHAR(25),route_no VARCHAR(6),
    stop_no VARCHAR(4), pick_area VARCHAR(6),pick_type VARCHAR(10),
    jurisdiction VARCHAR(6),carton_qty VARCHAR(2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ,CONSTRAINT id_pk PRIMARY KEY (id));"""
    # create table for this file
    mycursor.execute(mytable)
    cnct.commit()
    # create table and commit to database


def dat_assign(obj_dat):
    # split strings and assign them to dat files
    tem = obj_dat.line_dump
    # get line dump data
    obj_dat.rec_id = tem[0:8]
    obj_dat.route_num = tem[9:15]
    obj_dat.stop_num = tem[16:20]
    obj_dat.container_id = tem[21:36]
    obj_dat.assign_id = tem[37:62]
    obj_dat.pick_area = tem[63:69]
    obj_dat.pick_type = tem[70:80]
    obj_dat.juris = tem[105:111]
    obj_dat.carton_num = tem[112:114]
    # assign all fields for sql insertion
    return obj_dat


def dat_test(obj_dat):
    # test values by printing them for debugging purposes
    print(obj_dat.line_dump)
    print(obj_dat.rec_id + '\n' + 
    obj_dat.route_num + '\n' + 
    obj_dat.stop_num + '\n' + 
    obj_dat.container_id + '\n' + 
    obj_dat.assign_id + '\n' + 
    obj_dat.pick_area + '\n' + 
    obj_dat.pick_type + '\n' + 
    obj_dat.juris + '\n' + 
    obj_dat.carton_num)


def dat_insert(obj_dat, table_name):
    currentTimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = ("INSERT INTO " + table_name + """ (record_id,route_no,
    stop_no,container_id,assignment_id,pick_area,pick_type,
    jurisdiction,carton_qty,c_comp,a_comp,o_comp,r_comp,assign_name, status, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s)""")
    # setup table insertion
    val = (obj_dat.rec_id, obj_dat.route_num, obj_dat.stop_num, obj_dat.container_id, obj_dat.assign_id, obj_dat.pick_area, obj_dat.pick_type, obj_dat.juris, obj_dat.carton_num, 
    obj_dat.c_comp, obj_dat.a_comp, obj_dat.o_comp, obj_dat.r_comp, obj_dat.assign_name, None, currentTimeStamp, currentTimeStamp)
    # setup values for insertion
    mycursor.execute(sql, val)
    # insert the data into the table
    cnct.commit()
    # commit to database

     #TODO: this is where to call a new function to save to the route_statuses table
    #save_route_status(obj_dat)

    
    


def stamp_data(obj_dat):
    juris = obj_dat.juris.replace(" ", "0")
    cart = obj_dat.carton_num.replace(" ", "0")
    # trim and zero pad the vars
    data = juris + "," + "000000" + "," + "000000" + "," + cart
    return data
    # give it back

    
def dat_truncate(database_name):
    # deletes data older than 30 days and updates the id columns
    tables = []
    i = 0
    j = 0
    # initilize empty table array
    # query_fix_rows = ("ALTER " + tables[j] + " document MODIFY COLUMN document_id INT NOT NULL AUTO_INCREMENT;");
    # set query values for cursor
    mycursor.execute("USE " + database_name)
    mycursor.execute("SHOW TABLES")
    # get table names
    for (table_name,) in mycursor:
        # assign table names to table array
        tables.append(table_name)
        # inc
        i += 1
       
    for j in range(len(tables)):
        # does queries
        if tables[j] == "dat_master":
            # make sure not to delete the master table
            mycursor.execute("DELETE FROM " + tables[j] + " WHERE created_at < NOW() - INTERVAL " + fileDeleteInterval + " DAY AND updated_at IS null LIMIT 1000;")
            mycursor.execute("DELETE FROM " + tables[j] + " WHERE updated_at IS NOT null and updated_at < NOW() - INTERVAL " + fileDeleteInterval + " DAY LIMIT 1000;")
        else:
            mycursor.execute("DELETE FROM " + tables[j] + " WHERE created_at < NOW() - INTERVAL + " + fileDeleteInterval + " DAY AND updated_at IS null LIMIT 1000;")
            mycursor.execute("DELETE FROM " + tables[j] + " WHERE updated_at IS NOT null and updated_at < NOW() - INTERVAL " + fileDeleteInterval + " DAY LIMIT 1000;")
            mycursor.execute("select * from " + tables[j])
            mycursor.fetchall()
            # fetch all so we can get rows
            rows = str(mycursor.rowcount)
            rows = int(rows)
            # cast to string and then back to int so we can read the data
            if rows == 0:
                # if the table is empty
                mycursor.execute("DROP TABLE " + tables[j] + ";")
                print(tables[j] + " was deleted")
                # drop the table
        # executing queries
        print(tables[j] + " is being cleaned of data older than + " + fileDeleteInterval + " days")
        # make sure loop runs
        j += 1
        # inc
    cnct.commit()
    # commit changes


def insert_route_status(routeNumber, priorityNumber):
    try:
        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= database, 
            password= password 
        )

        cursor = connection.cursor()

        insertSQL = ("INSERT INTO route_statuses "
                    "(route, dock_door, trailer_number, priority, enable, status, date_at, created_at, updated_at) " 
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

        currentTimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        today = datetime.now().date().strftime('%Y-%m-%d')

        newRouteStatus = (routeNumber, "", "", priorityNumber, "Inactive", "Not Started", today, currentTimeStamp, currentTimeStamp)

        cursor.execute(insertSQL, newRouteStatus)
        connection.commit()
        
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()


def get_distinct_route_numbers():
    try:
        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= database, 
            password= password 
        )

        cursor = connection.cursor()

        getRouteStatusesSQL = "select distinct route from route_statuses" 
        #getRouteStatusesSQL = "select * from route_statuses"

        cursor.execute(getRouteStatusesSQL)
        
        processedResult = []
        result = cursor.fetchall()
        for row in result:
            processedResult.append(int(row[0]))

        cursor.close()
        connection.close()
        return processedResult
    except Exception as e:
        print(e)
        #connection.rollback()
        # exc_type, exc_value, exc_traceback = sys.exc_info()
        # lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        # exceptionMsg = exc_value.msg
        # exceptionDetails = ''.join('!! ' + line for line in lines)
        
        #GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)          
    finally:
        cursor.close()
        connection.close()

def get_route_statuses(numberLines):
    try:
        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= database, 
            password= password 
        )

        cursor = connection.cursor()

        #getRouteStatusesSQL = "select distinct route from route_statuses" 
        getRouteStatusesSQL = "select * from route_statuses"

        cursor.execute(getRouteStatusesSQL)
        
        result = cursor.fetchall()
        routeStatuses = []
        for row in result:
            routeStatus = route_status(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], numberLines)
            routeStatuses.append(routeStatus)
        
        cursor.close()
        connection.close()
        return routeStatuses #result
    except Exception as e:
        print(e)
        #connection.rollback()
        # exc_type, exc_value, exc_traceback = sys.exc_info()
        # lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        # exceptionMsg = exc_value.msg
        # exceptionDetails = ''.join('!! ' + line for line in lines)
        
        #GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)          
    finally:
        cursor.close()
        connection.close()

def update_route_status(routeStatus):
    try:
        connection = mysql.connector.connect(
            host= host, 
            user= user, 
            database= database, 
            password= password 
        )

        cursor = connection.cursor()

        #getRouteStatusesSQL = "select distinct route from route_statuses" 
        getRouteStatusesSQL = "UPDATE route_statuses SET priority = %s where id = %s"
    
        updateValues = (routeStatus.Priority, routeStatus.ID)

        cursor.execute(getRouteStatusesSQL, updateValues)

        connection.commit()
        
        # result = cursor.fetchall()
        # routeStatuses = []
        # for row in result:
        #     routeStatus = route_status(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], numberLines)
        #     routeStatuses.append(routeStatus)
        
        cursor.close()
        connection.close()
        #return routeStatuses #result
    except Exception as e:
        print(e)
        #connection.rollback()
        # exc_type, exc_value, exc_traceback = sys.exc_info()
        # lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        # exceptionMsg = exc_value.msg
        # exceptionDetails = ''.join('!! ' + line for line in lines)
        
        #GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)          
    finally:
        cursor.close()
        connection.close()


def do_everything():
    # put it all in a function
    working_path = input_path;  # replace with dir that 
    # path of python documents fold
    os.chdir(working_path)
    # go to the directory
    save_path_location = output_path
    # path to save new files to
    exists = False

    # init
    for fname in os.listdir('.'):
        print(fname)        
        if fname.endswith('.DAT'):
            # do stuff on the file
            exists = True
            # if its a .dat file then it exists
            break
        else:
            exists = False;
            # or it dodsent
            ### os.remove(working_path, fname);
            ### print("The file " + fname + " was not a .DAT file, or it is formatted incorrectly it has been deleted from" + working_path);
            # delete non dat files
    # do stuff if a file .true doesn't exist.
    if exists == True:
        assignment_name = fname.replace("ASSIGNMENT-","").replace(".DAT","")
        orig_file_name = fname;  # insert fancy functions to get name of file
        temp_name = orig_file_name[:-3]
        # get variable for file name and var for path
        orig_file_path = working_path + "\\" + orig_file_name
        # path to delete file after job is done
        save_path = save_path_location + "\\" + temp_name
        # create save path name
        if os.path.exists(save_path):
            print("This file has already run through the program, skipping and moving")
            if enabled == "1":
                hostLog.log(auth, domain, "DAT Converter to WXS", "Skipping File", "This file has already run through the program, skipping and moving")
            shutil.copyfile(orig_file_path, input_processed_path + "\\" + orig_file_name)
            os.remove(orig_file_path)
            # move original file
        else:
            os.mkdir(save_path)
            # create new folder for dat files
            #orig_dat_file = open(orig_file_name, "r")
            with open(orig_file_name, "r") as orig_dat_file:
            # openfile
                all_lines = orig_dat_file.readlines()
                # get read all lines variable
                num_lines = len(all_lines) #sum(1 for line in open(orig_file_name))

                existingRoutesStatuses = get_route_statuses(num_lines)
                distinctRouteNumbers = get_distinct_route_numbers()

                #Now, loop through the existingRouteStatuses and Update each record in the table with the new priority number
                for route in existingRoutesStatuses:
                    update_route_status(route)

                # get number of lines in the file
                print("Number of lines to be checked " + str(num_lines))
                if enabled == "1":
                    hostLog.log(auth, domain, "DAT Converter to WXS", "Numer Lines Checked", "Number of lines to be checked " + str(num_lines))
                # print number of lines
                table_name = temp_name[:-1].replace("-", "_")
                #dat_table_create(table_name)
                # create new table
                s = 0
                # variable for skipping lines
                ins = 0
                # variable for lines inserted
                priorityNumber = 0
                for j in range(num_lines):
                    temp_dat = obj_dat()
                    # create dat object for sql insertion
                    line_dump_data = all_lines[j] 
                    # get data from specific line 
                    temp_dat.line_dump = line_dump_data
                    # assign line to file
                    dat_assign(temp_dat)
                    # assing values for sql insertion
                    if temp_dat.rec_id == "        ":
                        pass
                    # get rid of blank line at the end of dat file
                    else:
                        ### dat_insert(temp_dat, table_name)
                        # insert data into mysql database
                        dat_insert(temp_dat, "dat_master")
                        # insert data into master table as well
                        
                        #save to the route status table. route_num in temp_dat has the route number
                        #save_route_status(temp_dat)
                        if temp_dat.route_num != '':
                            routeNumber = int(temp_dat.route_num.strip())
                            if routeNumber not in distinctRouteNumbers:
                                #insert into the route status table
                                #routeNumbersNotExisting.append(routeNumber)
                                priorityNumber += 1
                                insert_route_status(routeNumber, priorityNumber)


                    # dat_test(temp_dat)
                    # test those values
                    if (temp_dat.juris == "      ") and  (temp_dat.carton_num == "  "):
                        s += 1
                        # increment for number of file skipped
                    else:
                        if temp_dat.container_id == "":
                            pass;
                            # dont do anything
                        else:
                            ins += 1
                            # increment incrementer
                            new_file_name = temp_dat.container_id + ".DAT"
                            # get name for new dat file from line data 
                            new_name_complete = os.path.join(save_path, new_file_name)
                            # and name combined with save path
                            new_file_data = stamp_data(temp_dat)
                            # get data to be added to the new dat file
                            #new_file = open(new_name_complete, "w")
                            with open(new_name_complete, "w") as new_file:
                            # Creates a new file from the temp vars
                                new_file.write(new_file_data)
                                #new_file.close()
                            # print that data was inserted for files true
                print(str(table_name) + " had " + str(ins) + " files created and data inserted")
                print(str(s) + " files were skipped due to having blank carton and juris fields")
                if enabled == "1":
                    hostLog.log(auth, domain, "DAT Converter to WXS", "Data Inserted", str(table_name) + " had " + str(ins) + " files created and data inserted")
                    hostLog.log(auth, domain, "DAT Converter to WXS", "Files Skipped", str(s) + " files were skipped due to having blank carton and juris fields")
                # print that data was inserted for file
                #os.remove(orig_file_path)
                # delete original file

    else:
        print("No file present")
        # acknowledge no file is there


schedule.every(check_interval).seconds.do(do_everything)
# do it every x amount of  seconds
schedule.every(delete_interval).hours.do(dat_truncate, deploy_db)
# schedule checking and deleting of tables
while 1:
    schedule.run_pending()
    time.sleep(1)
    # don't run it 50 times over
    
atexit.register(os.chdir(input_path))
# return home at termination of script just in case
atexit.register(mycursor.close)
atexit.register(cnct.close)
# makes sure the connection is always terminated if the script is terminated
