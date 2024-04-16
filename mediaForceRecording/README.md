# Eagle Eye Cloud VMS RTSP Stream Player

This script allows you to fetch RTSP streams from the Eagle Eye Cloud VMS and play them using FFmpeg.

## Usage

1. Open the `config.py` file and enter your Eagle Eye Cloud VMS credentials:

    ```python
    username = "your-username"
    password = "your-password"
    ```
    The script will fetch the camera list, retrieve the RTSP streams, and play them for 5 seconds each.

2. Press `Ctrl+C` to stop the script.
