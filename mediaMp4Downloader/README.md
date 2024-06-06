# ee_api_v2_mp4_downloader# ee_api_v2_mp4_downloader

* please note that the code doesn't handle special characters within the password so if neede set a temp password with only letters and numbers.

# on mac:
install python

# Install the modules needed: 
python3 -m pip install requests
python3 -m pip install pytz

# usage:
python3 download.py -u "username" -p "password" -s 20240604000010.500 -e 20240605000010.500
python3 download.py -u "username" -p "password" -c 10106c94 -s 20240604000010.500 -e 20240605000010.500
python3 download.py -u "username" -p "password" -c 10106c94,10106c94,10106c94,10106c94,10106c94 -s 20240604000010.500 -e 20240605000010.500<br>
python3 download.py -u "username" -p "password" -c esn -s start_timestamp -e end_timestamp


# timestamp format:
20240605000010.500
YYYYMMDDHHMM00.000
