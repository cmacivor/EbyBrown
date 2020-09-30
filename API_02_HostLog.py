"""
Author: Robert Ward

Version: 1.0

"""

"""
m_type must not be longer than 15 characters

"""

# Imports

import requests
import python_config

# Deployment Variables

api = "/api/hostlogs/store"


# Function


def log(auth, domain, source, m_type, message):
    loggingConfig = python_config.read_logging_config()
    auth = loggingConfig.get('auth')
    domain = loggingConfig.get('domain')
    api = loggingConfig.get("api")
    url = domain + api

    parsedMessage = str(message).replace("b", "").replace("\\", "").replace("\x02", "").replace("\x03", "")

    data = {"source": source, "type": m_type, "message": parsedMessage}

    response = requests.post(url, json=data, allow_redirects=False)

    test = response

  


#test = log("Basic YWE6YQ==", "https://dev.pendantautomation.com", "WXS to Host", "Dock Scan Log Request", "Log Scan KD3101017-001")

#print(test)