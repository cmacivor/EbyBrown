
url = "http://10.22.56.11" + "/api/hostlogs/store"

import requests

#decodedMessage = message.decode('ascii')
#data = {"source": "test", "type": "test", "message": "00013|ADDCONTA|307604|1123|SC307604112-006|307604112|006003|SPLITCASE|113205|20"}
data = {"source": "test", "type": "test", "message": "00013|ADDCONTA|307604|1123"}
#data = {"source": "Craig Test", "type": "a test", "message": "a test msgggg"}

headers = {'Content-type': 'application/json', "Authorization": "Basic YWE6YQ=="}

response = requests.post(url, json=data, allow_redirects=False)

status = response