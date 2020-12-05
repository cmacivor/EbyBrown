"""
Author: Robert J. Ward

--Version: 1.0
    --- Initial Release

"""



# Imports

import requests
import python_config
from datetime import datetime
import time

# Deployment Variables

domain = "http://10.22.56.10:88/"
create_api = "api/popup-notifications/store"
delete_api = "api/popup-notifications/delete/screen/"
auth = "Basic YWE6YQ=="


def pop_up(a_message, a_color, a_backgroud_color, a_expire, a_screen_number):
    
    url = domain + create_api
    
    json = {"message" : a_message,
            "color" : a_color,
            "background_color" : a_backgroud_color,
            "expire" : a_expire,
            "screen_number" : a_screen_number
            }
    
    request = requests.post(url,
                            headers={"Authorization": auth, "Content-Type": "application/json", "Accept": "application/json"},
                            json=json
                            )
    
    data = request.json()
    
    #print(data)
    
    return data["id"]



def delete(screen):
    
    url = domain + delete_api
    
    request = requests.post(url + str(screen))
    
    data = request.json()
    
    #print(data)
    
    return "Done"

#print(pop_up("100 - 951<br>NO DOCK<br>PICS", "#E9EDF5", "#4287F5", "3600", "1"))

#print(delete(18))
