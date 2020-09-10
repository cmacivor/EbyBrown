""""
Author: Robert Ward

Version: 1.0

Created: 7.20.2020

Last Updated: 7.23.2020

"""

# Imports

import requests
import API_02_HostLog as hostLog
import API_03_httpStatusCodes as httpMessage

# Deployment Variables

api = "/api/eby-brown/door-scans/store?"

# Function

errorMessage = httpMessage.httpStatusCodes


def dock_scan_log(auth, domain, door_id, code, route, stop, reason):
    url = domain + api + "/&door_id=" + door_id + "&barcode=" + code + "&route=" + route + "&stop=" + stop + "&reason=" + reason
    request = requests.post(url, headers={"Authorization": auth, "Content-Type": "application/json", "Accept": "application/json"})
    hostLog.log(auth, domain, "PLC to WXS", "Dock Scan Log", "Log Scan " + code)
    httpcode = (str(request))[11:14]
    # print(httpCode)
    if httpcode == "201":
        data = request.json()
        hostLog.log(auth, domain, "WXS to PLC", "Log Confirm", "Logged Scan " + code)
        return data
    else:
        hostLog.log(auth, domain, "WXS to PLC", "Dock Scan Error", httpcode + " " + errorMessage[httpcode])
        return httpcode, errorMessage[httpcode]


# test = dock_scan_log("Basic YWE6YQ==", "https://dev.pendantautomation.com", "2", "KD3101017-012", "121", "100", "Double Read")

# print(test)
