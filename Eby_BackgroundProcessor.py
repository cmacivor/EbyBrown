"""
Author: Robert J. Ward
Changelog:
-- Version: 1.0 Robert J. Ward
    --- Initial Release


"""


import Eby_AssignmentStatus
import Eby_CountFlag
import Eby_PickAreaCopyPaste
import Eby_PickQty
import Eby_RouteStatus
import Eby_VerifyTrailersData
import time
import python_config
import mysql.connector


config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
wcsdatabase = config.get('wcsdatabase')
database = config.get('database')
password = config.get('password')


doors = [1, 2]


while True:

    try:

        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            password=password
        )

        cursor = connection.cursor()

        print(Eby_AssignmentStatus.update_assignment_status())

        print(Eby_CountFlag.count_flag())

        print(Eby_PickAreaCopyPaste.find_and_replace())

        print(Eby_PickQty.update_route_pick_qty())

        print(Eby_PickQty.update_verify_trailers_pick_qty())

        for door in doors:
            print(Eby_PickQty.update_early_late(door))

        print(Eby_RouteStatus.route_status())

        for door in doors:
            print(Eby_VerifyTrailersData.add_routes(door))

        print(Eby_VerifyTrailersData.freezer_cooler_picks())

        print(Eby_VerifyTrailersData.priority_update())

    except Exception as e:
        print(e)

    finally:
        connection.close()

    time.sleep(1)
