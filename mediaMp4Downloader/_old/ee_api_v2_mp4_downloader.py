import requests
import json
import pytz
import time
import timeit
from datetime import datetime, timedelta

# Added timer
start_time = timeit.default_timer()

# Global variables
with open('baseaaa.json') as user_file:
    file_contents = json.load(user_file)
    username = file_contents["username"]
    password = file_contents["password"]
    host = file_contents["host"]
    domain = file_contents["domain"]
    branding = ""  # Empty until authorized
    token = ""  # Empty until authenticated
    camid = file_contents["camid"]

# Start and end timestamp
timestamp = datetime.now(pytz.timezone('UTC')).strftime('%Y%m%d%H%M%S.000')  # UTC Timestamp
tz = pytz.timezone('Europe/Amsterdam')  # Amsterdam TimeZone
d = datetime.today() - timedelta(hours=0, minutes=50)  # Current time minus the specified duration
e = datetime.today() - timedelta(hours=0, minutes=5)  # Current time minus the specified duration
starttime = d.strftime('%Y%m%d%H%M%S.000')
endtime = e.strftime('%Y%m%d%H%M%S.000')
print("Start timestamp:", starttime)
print("End timestamp:", endtime)

# Translating the HTTP response codes to make the status messages easier to read
HTTP_STATUS_CODE = { 
    200: 'Request succeeded (200)', 
    201: 'Created, video download job has been created (201)',
    202: 'Pending, video download job is in progress (202)',
    301: 'Asset has been moved to a different archiver (301)',
    400: 'Bad Request, please check what you are sending (400)',
    401: 'Unauthorized due to invalid session cookie (401)', 
    403: 'Forbidden due to the user missing the necessary privileges (403)',
    404: 'Camera not provisioned / Camera get error (404)',
    410: 'Video is out of retention (410)',
    500: 'API had a problem (500)',
    502: 'Bad Gateway. We were unable to return the requested data. Please try again. (502)',
    503: 'Internal Camera Tag Maps Error. Please contact our support department. (503)',
    504: 'Gateway Timeout. We were unable to return the requested data inside our time limit. Please try again. (504)'
    }

s = requests.Session()

# Logging into Eagle Eye Cloud VMS
url = f"https://{host}/g/aaa/authenticate"
payload = {"username": username, "password": password}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

try:
    response = s.post(url, data=payload, headers=headers)
    response.raise_for_status()  # Raise an exception if the response status code is not 2xx

    print("Authenticate:", HTTP_STATUS_CODE[response.status_code])

    url = f"https://{host}/g/aaa/authorize"
    payload = {"token": response.json()['token']}

    response = s.post(url, data=payload, headers=headers)
    response.raise_for_status()

    branding = response.json()["active_brand_subdomain"]
    auth_key = s.cookies.get_dict()["auth_key"]

    print("Authorize: %s" % HTTP_STATUS_CODE[response.status_code])

except requests.exceptions.RequestException as e:
    print("Error: %s" % HTTP_STATUS_CODE[response.status_code], str(e))
    exit(1)


# MP4 download function
def mp4download():
    url = f"https://{branding}{domain}/asset/list/video?id={camid}&start_timestamp={starttime}&count=-1"
    payload = {}
    headers = {"auth_key": auth_key,
               "Cookie": "auth_key=" + auth_key
               }
    response = requests.request("GET", url, headers=headers, data=payload)
    st = response.json()[0]["s"]
    et = response.json()[0]["e"]
    if response.status_code == 200:
        name = camid + "start_"+st+"_end_"+et+"_video.mp4"
        url = f"https://{branding}{domain}/asset/play/video.mp4?id={camid}&start_timestamp=" + st +"&end_timestamp=" + et
        headers = {"auth_key": auth_key,
                   "Cookie": "auth_key=" + auth_key
                   }
        try:
            response = s.get(url, headers=headers)
            response.raise_for_status()
            if response.status_code == 200:
                with open(name, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            print("Download Mp4: %s" % HTTP_STATUS_CODE[response.status_code])
            elapsed = timeit.default_timer() - start_time
            print("time elapsed:", elapsed)
            return response.status_code
        
        except requests.exceptions.RequestException as e:
            print("Error: %s" % HTTP_STATUS_CODE[response.status_code], str(e))
        return None
        

# Main loop
while True:
    status_code = mp4download()
    time.sleep(1)
    if status_code == 200:
        print("Done")
        break
