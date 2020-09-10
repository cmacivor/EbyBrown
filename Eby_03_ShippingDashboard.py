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

