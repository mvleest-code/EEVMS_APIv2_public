import requests
import json
import subprocess
import time
from datetime import datetime, timedelta
import logging
import os
# Get the current directory
current_directory = os.getcwd()

# Set the log file path
log_file_path = os.path.join(current_directory, 'eagle_eye_vms.log')

# Setup logging as described above
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file_path,
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

s = requests.Session()  
username = ""
password = ""

def authenticate_and_authorize():
    url = "https://c013.eagleeyenetworks.com/g/aaa/authenticate"
    payload = {"username": username, "password": password}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    logging.debug(f"Sending authentication request to {url} for username {username}")
    response = s.post(url, data=payload, headers=headers)
    
    if response.status_code == 200:
        logging.info("Authentication successful")
        auth_token = response.json()['token']
        logging.debug(f"Received authentication token: {auth_token}")
        
        url = "https://c013.eagleeyenetworks.com/g/aaa/authorize"
        payload = {"token": auth_token}
        
        logging.debug("Sending authorization request")
        response = s.post(url, data=payload, headers=headers)
        
        if response.status_code == 200:
            auth_key = s.cookies.get_dict()["auth_key"]
            logging.info("Authorization successful, received auth key")
            return auth_key
        else:
            logging.error("Authorization failed")
    else:
        logging.error(f"Authentication failed. Status: {response.status_code}, Reason: {response.reason}")
    return None

auth_key = authenticate_and_authorize()

# Function to get the RTSP stream URL
def get_rtsp_stream(camera_id):
    url = f"https://c013.eagleeyenetworks.com/api/v2/media/cameras/{camera_id}/streams?A={auth_key}"
    headers = {'Authorization': 'Bearer ' + auth_key, 'Cookie': 'auth_key=' + auth_key}
    
    logging.debug(f"Requesting RTSP stream for camera ID {camera_id}")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        rtsp_url = response.json()["data"]["rtsp"]
        logging.info(f"Retrieved RTSP stream URL for camera {camera_id}")
        return rtsp_url
    elif response.status_code != 200:
        logging.warning("Authentication error, attempting to re-authenticate")
        new_auth_key = authenticate_and_authorize()
        if new_auth_key:
            headers['Authorization'] = 'Bearer ' + new_auth_key
            headers['Cookie'] = 'auth_key=' + new_auth_key
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                rtsp_url = response.json()["data"]["rtsp"]
                logging.info(f"Retrieved RTSP stream URL after re-authentication for camera {camera_id}")
                return rtsp_url
            else:
                logging.error("Failed to retrieve RTSP stream after re-authentication")
    logging.error(f"Failed to get RTSP stream for camera {camera_id}. Status: {response.status_code}")
    return None

# Function to play an RTSP stream for 5 seconds
def play_rtsp_stream(rtsp_url):
    if rtsp_url:
        command = ["ffmpeg", "-rtsp_transport", "tcp", "-i", rtsp_url, "-t", "5", "-f", "null", "-"]
        logging.debug(f"Executing FFmpeg command: {' '.join(command)}")
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            logging.info(f"Successfully played RTSP stream for 5 seconds: {rtsp_url}")
        except Exception as e:
            logging.error(f"Error playing stream: {e}")
    else:
        logging.error("No RTSP URL provided to play the stream")

# Main script to get camera list and schedule playback
def main():
    logging.info("Starting main function to fetch camera list and manage RTSP streams.")
    """
    Main script to fetch camera list, retrieve RTSP streams, and play them.
    """
    url = "https://c013.eagleeyenetworks.com/g/device/list?t=camera"
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
            logging.info(f"Fetching RTSP stream for {camera['camera_name']}")
            rtsp_url = get_rtsp_stream(camera["camera_id"])
            logging.info(f"Playing {camera['camera_name']} stream for 5 seconds")
            play_rtsp_stream(rtsp_url)
        
        # Wait for 10 seconds before replaying streams
        time_to_wait = 10
        logging.info(f"Waiting for {time_to_wait} seconds before replaying streams.")
        time.sleep(time_to_wait)
        logging.info("Completed one full cycle of fetching and playing streams. Waiting to restart.")

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error("An error occurred: %s", e)
            continue
