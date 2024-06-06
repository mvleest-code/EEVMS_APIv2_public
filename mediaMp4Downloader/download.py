import argparse
import requests
import pytz
from datetime import datetime, timedelta
import time
import os
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def authenticate_and_authorize(username, password):
    session = requests.Session()
    auth_url = "https://login.eagleeyenetworks.com/g/aaa/authenticate"
    auth_payload = {"username": username, "password": password}
    auth_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        auth_response = session.post(auth_url, data=auth_payload, headers=auth_headers)
        auth_response.raise_for_status()

        if auth_response.status_code == 200:
            token = auth_response.json()['token']
            authz_url = "https://login.eagleeyenetworks.com/g/aaa/authorize"
            authz_payload = {"token": token}
            authz_response = session.post(authz_url, data=authz_payload, headers=auth_headers)
            authz_response.raise_for_status()

            branding = authz_response.json()["active_brand_subdomain"]
            account_id = authz_response.json()["active_account_id"]
            auth_key = session.cookies.get_dict()["auth_key"]
            logging.info(f"Authenticated and authorized successfully. Account ID: {account_id}, Branding: {branding}")

            return branding, auth_key, account_id
        else:
            raise Exception("Authorization failed")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to authenticate or authorize: {e}")
        raise Exception("Authentication or authorization failed")

def get_camera_ids(branding, auth_key):
    url = f"https://{branding}.eagleeyenetworks.com/g/device/list"
    headers = {'Cookie': f'auth_key={auth_key}'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        cameras = [(cam[1], cam[2]) for cam in response.json() if cam[3] == "camera"]
        return dict(cameras)
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve cameras: {e}")
        raise

def download_video(branding, auth_key, camera_id, start_timestamp, end_timestamp):
    folder_path = os.path.join("videos", camera_id)
    os.makedirs(folder_path, exist_ok=True)
    url = f"https://{branding}.eagleeyenetworks.com/asset/play/video.mp4"
    params = {
        "id": camera_id,
        "start_timestamp": start_timestamp,
        "end_timestamp": end_timestamp
    }
    headers = {'Cookie': f'auth_key={auth_key}'}

    try:
        response = requests.get(url, params=params, headers=headers, stream=True)
        if response.status_code == 200:
            total_length = response.headers.get('content-length')
            if total_length is None:  # no content length header
                logging.info("Downloading video (unknown total size)...")
            else:
                dl = 0
                total_length = int(total_length)
                filename = f"{folder_path}/{camera_id}_{start_timestamp}_{end_timestamp}.mp4"
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            dl += len(chunk)
                            f.write(chunk)
                            done = int(50 * dl / total_length)
                            logging.info(f"\rDownloading: [{'=' * done}{' ' * (50-done)}] {dl}/{total_length} bytes")
            logging.info(f"Downloaded video for camera {camera_id} to {filename}.")
        else:
            logging.error(f"Failed to download video: HTTP {response.status_code} - {response.reason}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error while downloading video: {e}")

def calculate_chunks(start_timestamp, end_timestamp):
    chunks = []
    current_timestamp = start_timestamp
    while current_timestamp < end_timestamp:
        chunk_end_timestamp = current_timestamp + timedelta(hours=8)
        if chunk_end_timestamp > end_timestamp:
            chunk_end_timestamp = end_timestamp
        chunks.append((current_timestamp, chunk_end_timestamp))
        current_timestamp = chunk_end_timestamp
    return chunks

def main(args):
    try:
        branding, auth_key, account_id = authenticate_and_authorize(args.username, args.password)
        camera_ids = args.camera_ids.split(',') if args.camera_ids else get_camera_ids(branding, auth_key).keys()

        # Parse timestamps with milliseconds precision
        start_datetime = datetime.strptime(args.start, '%Y%m%d%H%M%S.%f')
        end_datetime = datetime.strptime(args.end, '%Y%m%d%H%M%S.%f')

        for cam_id in camera_ids:
            chunks = calculate_chunks(start_datetime, end_datetime)
            for start_chunk, end_chunk in chunks:
                # Format the timestamps to include only up to milliseconds
                start_chunk_str = start_chunk.strftime('%Y%m%d%H%M%S.%f')[:-3]  # Truncate to milliseconds
                end_chunk_str = end_chunk.strftime('%Y%m%d%H%M%S.%f')[:-3]      # Truncate to milliseconds

                logging.info(f"Downloading video from {start_chunk_str} to {end_chunk_str} for camera {cam_id}")
                download_video(branding, auth_key, cam_id, start_chunk_str, end_chunk_str)
    except Exception as e:
        logging.error(f"An error occurred during the main execution: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download videos from Eagle Eye Cameras.")
    parser.add_argument("-u", "--username", required=True, help="Username for authentication")
    parser.add_argument("-p", "--password", required=True, help="Password for authentication")
    parser.add_argument("-c", "--camera_ids", help="Comma-separated camera IDs (optional), if none provided, will fetch all available.")
    parser.add_argument("-s", "--start", required=True, help="Start timestamp in YYYYMMDDHHMMSS.SSS format")
    parser.add_argument("-e", "--end", required=True, help="End timestamp in YYYYMMDDHHMMSS.SSS format")

    args = parser.parse_args()
    main(args)