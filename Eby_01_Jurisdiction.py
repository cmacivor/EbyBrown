""""
Author: Robert Ward

Version: 1.0

Created: 7.20.2020

Last Updated: 7.23.2020

"""

# Imports

import requests
import  API_02_HostLog as hostLog
import API_03_httpStatusCodes as httpMessage

# Deployment Variables

api = "/api/eby-brown/jurisdiction/filter?code="

# Function

errorMessage = httpMessage.httpStatusCodes


def lookup(auth, domain, jurisdiction_code):
    url = domain + api + jurisdiction_code
    request = requests.get(url, headers={"Authorization": auth, "Content-Type": "application/json", "Accept": "application/json"})
    #hostLog.log(auth, domain, "PLC to WXS", "Lane Request", "Request for " + jurisdiction_code)
    httpcode = (str(request))[11:14]
    # print(httpCode)
    if httpcode == "200":
        data = request.json()
        lanes = ("".join(str(data))).replace("[", "").replace("]", "")
        #hostLog.log(auth, domain, "WXS to PLC", "Lane Reply", "Lane(s) " + lanes)
        return httpcode, lanes
    else:
        #hostLog.log(auth, domain, "WXS to PLC", "Error Reply", httpCode + " " + errorMessage[httpcode])
        return httpcode, errorMessage[httpcode]


# test = jurisdiction("Basic YWE6YQ==", "https://dev.pendantautomation.com", "123456")

# print(test)
