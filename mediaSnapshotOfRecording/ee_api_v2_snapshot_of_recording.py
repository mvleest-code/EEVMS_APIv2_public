import requests
import json
import pytz
from datetime import datetime, timedelta
import time

## Global variables:
with open('baseaaa.json') as user_file:
        file_contents = json.load(user_file)
        username  = file_contents["username"]
        password  = file_contents["password"]
        host      = file_contents["host"]
        domain    = file_contents["domain"]
        branding  = "" ## empty until authorized
        token     = "" ## empty until authentiated
        camid     = file_contents["camid"]
        
## Start and end timestamp:
        timestamp = (datetime.now(pytz.timezone('UTC')).strftime('%Y%m%d%H%M%S.000')) # UTC Timestamp
        tz        = pytz.timezone('Europe/Amsterdam') # Amsterdam TimeZone
        d         = datetime.today() - timedelta(hours=2, minutes=50)
        e         = datetime.today() - timedelta(hours=2, minutes=50)
        starttime = d.strftime('%Y%m%d%H%M%S.000')
        #starttime = '20230521124512.630'
        endtime   = e.strftime('%Y%m%d%H%M%S.000')
        #starttime = timestamp # Start TimeStamp
        #endtime   = (datetime.now(tz=tz).strftime('%Y%m%d%H%M%S.000')) # End_Time = start_time + 1 hour

s = requests.Session()  

## Logging into Eagle Eye Cloud VMS ##     
url = "https://" + host + "/g/aaa/authenticate"
payload = {"username": username,
           "password": password}
headers = {'Content-Type': 'application/x-www-form-urlencoded'
        }
response = s.post(url, data=payload, headers=headers)
if response.status_code == 200:
        print ("authenticate....",response.status_code, response.reason)
        url       = "https://" + host + "/g/aaa/authorize"
        payload   = {"token": response.json()['token']}
        headers   = {'Content-Type': 'application/x-www-form-urlencoded'
                }
        response  = s.post(url, data=payload, headers=headers)
        branding  = response.json()["active_brand_subdomain"]
        auth_key  = s.cookies.get_dict()["auth_key"]
        print ("authorize.......",response.status_code, response.reason)
        
## Snapshot api testing
def snapshot():
  url = "https://"+ branding + ".eagleeyenetworks.com/api/v2/media/"+ camid +"/Snapshot?timestamp=" + starttime

  payload = {}
  headers = {
    'auth_key': auth_key,
    'Cookie': 'auth_key='+ auth_key
  }

  response = s.request("GET", url, headers=headers, data=payload)
  if response.status_code == 200:
            # this is the actual media object, save to a file
            local_filename = 'snapshot.jpeg'
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=256): 
                    if chunk: 
                        f.write(chunk)
                    return response.status_code              
  elif response.status_code != 200:
    print (response.status_code," : retrying in 10 seconds")
    time.sleep(10) 
    return response.status_code
  print(response.text)

# Main loop
while True:
    status_code = snapshot()
    if status_code == 200:
        print("Done")
        break
