import requests
import json
import subprocess
import time
from datetime import datetime, timedelta

s = requests.Session()  

## Logging into Eagle Eye Cloud VMS ##     
username = ""
password = ""

def authenticate_and_authorize():
    """
    Authenticates and authorizes the user with the Eagle Eye Cloud VMS.
    Returns the authentication key if successful, None otherwise.
    """
    url = f"https://login.eagleeyenetworks.com/g/aaa/authenticate"
    payload = {
        "username": username,
        "password": password
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = s.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        print("authenticate....", "response:", response.status_code, response.reason)
        url = f"https://login.eagleeyenetworks.com/g/aaa/authorize"
        payload = {"token": response.json()['token']}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = s.post(url, data=payload, headers=headers)
        auth_key = s.cookies.get_dict()["auth_key"]
        print("authorize.......", "response:", response.status_code, response.reason)
        return auth_key
    else:
        print("Failed to authenticate and authorize.")
        return None

auth_key = authenticate_and_authorize()

# Function to get the RTSP stream URL
def get_rtsp_stream(camera_id):
    """
    Retrieves the RTSP stream URL for a given camera ID.
    Returns the RTSP URL if successful, None otherwise.
    """
    url = f"https://login.eagleeyenetworks.com/api/v2/media/cameras/{camera_id}/streams?A={auth_key}"

    headers = {
        'Authorization': 'Bearer ' + auth_key,
        'Cookie': 'auth_key=' + auth_key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        rtsp_url = response_data["data"]["rtsp"]
        return rtsp_url
    else:
        print(f"Failed to get RTSP stream for camera {camera_id}")
        return None

# Function to play an RTSP stream for 5 seconds
def play_rtsp_stream(rtsp_url):
    """
    Plays an RTSP stream for 5 seconds using FFmpeg.
    """
    if rtsp_url:
        try:
            # FFmpeg command to play stream for 5 seconds
            command = ["ffmpeg", "-rtsp_transport", "tcp", "-i", rtsp_url, "-t", "5", "-f", "null", "-"]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except Exception as e:
            print(f"Error playing stream: {e}")
    else:
        print("No RTSP URL provided.")

# Main script to get camera list and schedule playback
def main():
    """
    Main script to fetch camera list, retrieve RTSP streams, and play them.
    """
    url = "https://login.eagleeyenetworks.com/g/device/list?t=camera"
    headers = {
        'Authorization': 'Bearer ' + auth_key,
        'Cookie': 'auth_key=' + auth_key
    }
    response = requests.get(url, headers=headers)
    cameras = json.loads(response.text)

    # Filter for cameras with "ATTD"
    filtered_cameras = [{
        "account_id": camera[0],
        "camera_id": camera[1],
        "camera_name": camera[2]
    } for camera in cameras if camera[5] == "ATTD"]

    while True:
        start_time = datetime.now()
        for camera in filtered_cameras:
            print(f"Fetching RTSP stream for {camera['camera_name']}")
            rtsp_url = get_rtsp_stream(camera["camera_id"])
            print(f"Playing {camera['camera_name']} stream for 5 seconds")
            play_rtsp_stream(rtsp_url)
        
        # Wait for 10 seconds before replaying streams
        time_to_wait = 10
        print(f"Waiting for {time_to_wait} seconds before replaying streams.")
        time.sleep(time_to_wait)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
