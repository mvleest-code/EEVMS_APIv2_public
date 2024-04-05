EE-LDS-TESTING<br>
<br>
ADD USERNAME AND PASSWORD TO RUN<br>
username   = "" <br>
password   = ""<br>
<br>
Purpose of this script:<br>
Test Eagle Eye Local Display Station /g/device and /g/device/rtsp api calls:<br>
<br>
Result of the script should look something like this;<br>

```
/g/device 200 {'id': '100c96fc'}
Get Camera RTSP error {'id': '100c96fc'} 500
/g/device 200 {'id': '100207f5'}
/g/device/rtsp 200 {'id': '100207f5'}
/g/device 200 {'id': '100b1529'}
/g/device/rtsp 200 {'id': '100b1529'}
/g/device 200 {'id': '1007ccd8'}
/g/device/rtsp 200 {'id': '1007ccd8'}
/g/device 200 {'id': '1008a415'}
/g/device/rtsp 200 {'id': '1008a415'}
/g/device 200 {'id': '10096def'}
/g/device/rtsp 200 {'id': '10096def'}
/g/device 200 {'id': '1006ab89'}
/g/device/rtsp 200 {'id': '1006ab89'}
/g/device 200 {'id': '100fbe9f'}
/g/device/rtsp 200 {'id': '100fbe9f'}
/g/device 200 {'id': '1008aa93'}
/g/device/rtsp 200 {'id': '1008aa93'}
/g/device 200 {'id': '100de948'}
/g/device/rtsp 200 {'id': '100de948'}
End of the script 200
```
<br>
In this usecase we have one camera that was offline so it failed with error 500:<br>

```
/g/device 200 {'id': '100c96fc'}
Get Camera RTSP error {'id': '100c96fc'} 500
```
