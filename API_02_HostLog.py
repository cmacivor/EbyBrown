"""
Author: Robert Ward

Version: 1.0

"""

"""
m_type must not be longer than 15 characters

"""

# Imports

import requests

# Deployment Variables

api = "/api/hostlogs/store"


# Function


def log(auth, domain, source, m_type, message):
    url = domain + api
    request = requests.post(url, headers={"Authorization": auth}, json={"source": source, "type": m_type, "message": message})
    data = request.json()
    return request, data


#test = log("Basic YWE6YQ==", "https://dev.pendantautomation.com", "WXS to Host", "Dock Scan Log Request", "Log Scan KD3101017-001")

#print(test)