import requests
import json
import os
import pytz
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import timeit
from tqdm import tqdm
import logging
import time

s = requests.Session()
start_timer = timeit.default_timer()  # Start timing here
# Set up logging

logging.basicConfig(filename='mediaBatchFLVDownload.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

## Logging into Eagle Eye Cloud VMS ##     
username = ""
password = ""
branding = "login"

tz = pytz.timezone('UTC')
minutes_ago = 10
d = datetime.now(tz) - timedelta(minutes=minutes_ago)
e = datetime.now(tz)
start_time = d.strftime('%Y%m%d%H%M%S.000')
end_time = e.strftime('%Y%m%d%H%M%S.000')

print(f"Download FLV video, get list from {minutes_ago} minutes ago and start the download")
print("Start timestamp:", start_time)
print("End timestamp:", end_time)

def authenticate_and_authorize():
    url = "https://login.eagleeyenetworks.com/g/aaa/authenticate"
    payload = {"username": username, "password": password}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = s.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        url = "https://login.eagleeyenetworks.com/g/aaa/authorize"
        payload = {"token": response.json()['token']}
        response = s.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            auth_key = s.cookies.get_dict()["auth_key"]
            return auth_key
        else:
            print("Failed to authorize.")
            logger.error('Failed to authorize.')
            return None
    else:
        print("Failed to authenticate.")
        logger.error('Failed to authenticate.')
        return None

auth_key = authenticate_and_authorize()

def get_filtered_cameras(auth_key):
    download_folder = os.path.join(os.getcwd(), "download")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    url = "https://login.eagleeyenetworks.com/g/device/list?t=camera"
    headers = {'Authorization': f'Bearer {auth_key}', 'Cookie': f'auth_key={auth_key}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        cameras = json.loads(response.text)
        filtered_cameras = [{"account_id": camera[0], "camera_id": camera[1], "camera_name": camera[2]} for camera in cameras if "ATTD" in camera]
        return filtered_cameras, download_folder
    else:
        print(f"Failed to fetch cameras, status: {response.status_code}")
        logger.error(f"Failed to fetch cameras, status: {response.status_code}")
        return [], ""

filtered_cameras, download_folder = get_filtered_cameras(auth_key)

def download_single_video(download_details):
    camera_id, camera_name, video_info, camera_folder, headers = download_details
    start_timestamp = video_info["s"]
    end_timestamp = video_info["e"]
    download_url = f"https://login.eagleeyenetworks.com/asset/play/video.flv?id={camera_id}&start_timestamp={start_timestamp}&end_timestamp={end_timestamp}"
    download_response = requests.get(download_url, headers=headers, stream=True)
    if download_response.status_code == 200:
        file_path = os.path.join(camera_folder, f"{camera_id}_start_{start_timestamp}_end_{end_timestamp}_video.flv")
        if os.path.exists(file_path):
            logger.info(f"Skipping download for {camera_name} {start_timestamp} - File already exists")
            return
        total_size = int(download_response.headers.get('content-length', 0))
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Downloading video: {camera_name} {start_timestamp}", leave=False) as progress_bar:
            with open(file_path, 'wb') as f:
                for chunk in download_response.iter_content(chunk_size=1024):
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        logger.info(f"Successfully downloaded video for {camera_name} {start_timestamp}")
    else:
        logger.error(f"Failed to download video for {camera_name}, response: {download_response.status_code}")
        print(f"Failed to download video for {camera_name}, response: {download_response.status_code}")

def download_video(camera_id, camera_name):
    try:
        camera_folder = os.path.join(download_folder, camera_name.replace("/", "_"))
        if not os.path.exists(camera_folder):
            os.makedirs(camera_folder)
        video_list_url = f"https://login.eagleeyenetworks.com/asset/list/video?id={camera_id}&start_timestamp={start_time}&end_timestamp={end_time}&count=50"
        headers = {'Authorization': f'Bearer {auth_key}', 'Cookie': f'auth_key={auth_key}'}
        video_list_response = requests.get(video_list_url, headers=headers)
        if video_list_response.status_code == 200 and video_list_response.json():
            videos = video_list_response.json()
            download_details = [(camera_id, camera_name, video, camera_folder, headers) for video in videos]
            with ThreadPoolExecutor(max_workers=10) as executor:
                list(tqdm(executor.map(download_single_video, download_details), total=len(videos), desc=f"Downloading videos for {camera_name}", leave=False))
        else:
            logger.error(f"No videos found for {camera_name}, response: {video_list_response.status_code}")
            print(f"No videos found for {camera_name}, response: {video_list_response.status_code}")
    except Exception as e:
        print(f"Exception in downloading video for {camera_name}: {e}")
        logger.error('Failed to download: %s', e)

def download_videos_for_all_cameras(filtered_cameras):
    while True:
        with ThreadPoolExecutor(max_workers=20) as executor:
            list(tqdm(executor.map(lambda x: download_video(x["camera_id"], x["camera_name"]), filtered_cameras), total=len(filtered_cameras), desc="Overall progress"))
        time.sleep(60)  # Wait for 1 minute before the next run

download_videos_for_all_cameras(filtered_cameras)

elapsed = timeit.default_timer() - start_timer
print("Script execution time:", elapsed)
