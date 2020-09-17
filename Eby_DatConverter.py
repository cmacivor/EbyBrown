'''
Pendant Automation
Contact:(410) 939-7707

@author: Jeremy Scheuerman

@version: 1.7

Created:6/--/20

Last Updated:7/29/20

Changes:fixed line at the end
'''

'''
Secondary Variables (for quick access)
deploy_db_user = 'Pendant';
deploy_db_pass = 'Pendant0505';
deploy_db_host = 'localhost';
deploy_db_user = 'PaulCastro@eby-brown-assignment-mysql';
deploy_db_pass = 'PC$My$SQL88';
deploy_db_host = 'eby-brown-assignment-mysql.mysql.database.azure.com';
'''
# /home/jeremy/Documents/Pendant_automation/Lucas_Docs
import os, sys;
# get get os stuff and file mod functions
import mysql.connector;
from mysql.connector import (connection);
# get mysql stuff
import time;
import schedule;
# import for timer stuff
import atexit;
# write code that happens if the script is terminated
 
# deployment variables
deploy_input_path = "/home/jeremy/Documents/Pendant_automation/Lucas_Docs/dat_converter/input_file";                        
# assign path of folder where the dat files are supposed to be   
deploy_output_path = "/home/jeremy/Documents/Pendant_automation/Lucas_Docs/dat_converter/output_files/";
# assign path to save output with dat files folder
deploy_check_interval = 15;
# amount of time to wait in between next check IN SECONDS

# database file located dat_converter/database file
deploy_db_user = 'PaulCastro@eby-brown-assignment-mysql';
deploy_db_pass = 'PC$My$SQL88';
deploy_db_host = 'eby-brown-assignment-mysql.mysql.database.azure.com';
# insert database infromation

cnct = connection.MySQLConnection(user=deploy_db_user, password=deploy_db_pass, host=deploy_db_host);                                                        
# establish connection names are temporary until mysql is figured out
print("Connected to database succesfully");
mycursor = cnct.cursor();
# get cursor
mycursor.execute("CREATE DATABASE IF NOT EXISTS Assignment");
# create if it isnt there
mycursor.execute("USE Assignment;");
# switch to right database


class obj_dat:
    # create object for easier organization and database management
    # here are the fields for the mysql table
    line_dump = "";
    # place holder for line dump dat
    rec_id = "        ";
    # record identifier
    # max length 8 
    route_num = "      ";
    # route number
    # max length 6
    stop_num = "    ";
    # stop number
    # max length 4
    container_id = "               ";
    # specific container for this pick 
    # max length 15
    assign_id = "                         ";
    # assignment id for container
    # max length 25
    pick_area = "      ";
    # concotatenation of 3 digit stype and 3 digit pick area 
    # max length of 6
    pick_type = "          ";
    # for full cas a description will be sent if no description it will just say full case
    # for split case it will always say split case
    # max length of 10
    juris = "      ";
    # neede for cig stamping, if not cigs then its spaces, 
    # max length of 6
    carton_num = "  ";
    # number of cigs in container, if not , spaces
    # max length 2


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
    mycursor.execute(mytable);
    cnct.commit();
    # create table and commit to database


def dat_assign(obj_dat):
    # split strings and assign them to dat files
    tem = obj_dat.line_dump;
    # get line dump data
    obj_dat.rec_id = tem[0:8];
    obj_dat.route_num = tem[9:15];
    obj_dat.stop_num = tem[16:20];
    obj_dat.container_id = tem[21:36];
    obj_dat.assign_id = tem[37:62];
    obj_dat.pick_area = tem[63:69];
    obj_dat.pick_type = tem[70:80];
    obj_dat.juris = tem[105:111];
    obj_dat.carton_num = tem[112:114];
    # assign all fields for sql insertion
    return obj_dat;


def dat_test(obj_dat):
    # test values by printing them for debugging purposes
    print(obj_dat.line_dump);
    print(obj_dat.rec_id + '\n' + 
    obj_dat.route_num + '\n' + 
    obj_dat.stop_num + '\n' + 
    obj_dat.container_id + '\n' + 
    obj_dat.assign_id + '\n' + 
    obj_dat.pick_area + '\n' + 
    obj_dat.pick_type + '\n' + 
    obj_dat.juris + '\n' + 
    obj_dat.carton_num);


def dat_insert(obj_dat, table_name):
    sql = ("INSERT INTO " + table_name + """ (record_id,route_no,
    stop_no,container_id,assignment_id,pick_area,pick_type,
    jurisdiction,carton_qty) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""");
    # setup table insertion
    val = (obj_dat.rec_id, obj_dat.route_num, obj_dat.stop_num, obj_dat.container_id, obj_dat.assign_id, obj_dat.pick_area, obj_dat.pick_type, obj_dat.juris, obj_dat.carton_num);
    # setup values for insertion
    mycursor.execute(sql, val);
    # insert the data into the table
    cnct.commit();
    # commit to database


def stamp_data(obj_dat):
    juris = obj_dat.juris.replace(" ", "0");
    cart = obj_dat.carton_num.replace(" ", "0");
    # trim and zero pad the vars
    data = juris + "," + "000000" + "," + "000000" + "," + cart;
    return data;
    # give it back
    

def do_everything():
    # put it all in a functiony
    working_path = deploy_input_path;  # replace with dir that 
    # path of python documents fold
    os.chdir(working_path);
    # go to the directory
    save_path_location = deploy_output_path
    # path to save new files to
    exists = False;
    # init3
    for fname in os.listdir('.'):
        print(fname)
        if fname.endswith('.DAT'):
            # do stuff on the file
            exists = True;
            # if its a .dat file then it exists
            break;
        else:
            exists = False;
            # or it dodsent
            os.remove(working_path, fname);
            print("The file " + fname + " was not a .DAT file, or it is formatted incorrectly it has been deleted from" + working_path);
            # delete non dat files
    # do stuff if a file .true doesn't exist.
    if exists == True:
        orig_file_name = fname;  # insert fancy functions to get name of file
        temp_name = orig_file_name[:-3];
        # get variable for file name and var for path
        orig_file_path = working_path + "/" + orig_file_name;
        # path to delete file after job is done
        save_path = save_path_location + "/" + temp_name;
        # create save path name
        if os.path.exists(save_path):
            print("This file has already run through the program, skipping and deleting")
            os.remove(orig_file_path);
            # delete original file
        else:
            os.mkdir(save_path);
            # create new folder for dat files
            orig_dat_file = open(orig_file_name, "r");
            # openfile
            all_lines = orig_dat_file.readlines();
            # get read all lines variable
            num_lines = sum(1 for line in open(orig_file_name));
            # get number of lines in the file
            print("Number of lines to be checked " + str(num_lines));
            # print number of lines
            table_name = temp_name[:-1].replace("-", "_");
            dat_table_create(table_name);
            # create new table
            s = 0;
            # variable for skipping lines
            ins = 0;
            # variable for lines inserted
            for j in range(num_lines):
                temp_dat = obj_dat();
                # create dat object for sql insertion
                line_dump_data = all_lines[j];
                # get data from specific line 
                temp_dat.line_dump = line_dump_data;
                # assign line to file
                dat_assign(temp_dat);
                # assing values for sql insertion
                if temp_dat.rec_id == "        ":
                    pass;
                # get rid of blank line at the end of dat file
                else:
                    dat_insert(temp_dat, table_name);
                    # insert data into mysql database
                
                # dat_test(temp_dat);
                # test those values
                if (temp_dat.juris == "      ") and  (temp_dat.carton_num == "  "):
                    s += 1;
                    # increment for number of file skipped
                else:
                    if temp_dat.container_id == "":
                        pass;
                        # dont do anything
                    else:
                        ins += 1;
                        # increment incrementer
                        new_file_name = temp_dat.container_id + ".DAT";
                        # get name for new dat file from line data 
                        new_name_complete = os.path.join(save_path, new_file_name);
                        # and name combined with save path
                        new_file_data = stamp_data(temp_dat);
                        # get data to be added to the new dat file
                        new_file = open(new_name_complete, "w");
                        # Creates a new file from the temp vars
                        new_file.write(new_file_data);
                        new_file.close();
                        # print that data was inserted for files true
            print(str(table_name) + " had " + str(ins) + " files created and data inserted");
            print(str(s) + " files were skipped due to having blank carton and juris fields");
            # print that data was inserted for file
            os.remove(orig_file_path);
            # delete original file
    else:
        print("No file present");
        # acknowlege no file is there


schedule.every(deploy_check_interval).seconds.do(do_everything);
# do it every x amount of  seconds
while 1:
    schedule.run_pending();
    time.sleep(1);
    # don't run it 50 times over
    
atexit.register(os.chdir(deploy_input_path));
# return home at termination of script just in case
atexit.register(mycursor.close);
atexit.register(cnct.close);
# makes sure the connection is always terminated if the script is terminated

