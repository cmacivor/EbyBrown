""""
Author: Robert Ward

Version: 1.0

Created: 7.23.2020

Last Updated: 7.23.2020

Changes:

"""

# Imports

import requests
import API_02_HostLog as hostLog
import API_03_httpStatusCodes as httpMessage

# Deployment Variables

create_api = "/api/eby-brown/verify-trailers/create?"
update_api = "/api/eby-brown/verify-trailers/update/"


# Function

errorMessage = httpMessage.httpStatusCodes


def trailer_verify(auth, domain, route, door_id, trailer_id, freezer, cooler, dry, verify):
    url = domain + create_api + "door_id=" + door_id + "&dock_door_number= " + door_id + "&route=" + route + "&trailer_id=" + trailer_id + "&freezer_container=" + freezer + "&cooler_container=" + cooler + "&dry_container=" + dry + "&verify=" + verify
    request = requests.post(url, headers={"Authorization": auth, "Content-Type": "application/json", "Accept": "application/json"})
    hostLog.log(auth, domain, "PLC to WXS", "Create Trailer Route", "Route/Trailer " + route + "/" + trailer_id)
    httpcode = (str(request))[11:14]
    # print(httpCode)
    if httpcode == "201":
        data = request.json()
        hostLog.log(auth, domain, "WXS to PLC", "Route Log", "Logged  " + route + "/" + trailer_id)
        return data
    else:
        hostLog.log(auth, domain, "WXS to PLC", "Route Log Error", httpcode + " " + errorMessage[httpcode])
        return httpcode, errorMessage[httpcode]


test = trailer_verify("Basic YWE6YQ==", "https://dev.pendantautomation.com", "121", "1", "4567", "0", "2", "42", "0")

print(test)



def trailer_update(auth, domain, route, trailer_id, verify, record_id):
    url = domain + update_api + record_id  + "?" + "verify=" + verify
    request = requests.post(url, headers={"Authorization": auth, "Content-Type": "application/json", "Accept": "application/json"})

    if verify == "1":
        hostLog.log(auth, domain, "PLC to WXS", "Update Trailer Route", route + "/" + trailer_id + " verify")
    else:
        hostLog.log(auth, domain, "PLC to WXS", "Update Trailer Route", route + "/" + trailer_id + " mismatch")

    httpcode = (str(request))[11:14]
    # print(httpCode)
    if httpcode == "200":
        data = request.json()

        if verify == "1":
            hostLog.log(auth, domain, "WXS to PLC", "Route Updated", route + "/" + trailer_id + " verified")
        else:
            hostLog.log(auth, domain, "WXS to PLC", "Route Updated", route + "/" + trailer_id + " mismatched")

        return data
    else:
        hostLog.log(auth, domain, "WXS to PLC", "Route Log Error", httpcode + " " + errorMessage[httpcode])
        return httpcode, errorMessage[httpcode]


#test = trailer_update("Basic YWE6YQ==", "https://dev.pendantautomation.com", "121", "4567", "1", "29")

#print(test)
