# get_geolocation
Get your geolocation (longitude, latitude) with wlan (Wifi) or IP information. Also create wlan log and hereAPI around area Image

## Requirement
1. A device can get wifi signal, if not, this scripts using IP info.
2. HERE API key.
3. python 3 environment (with requests>=2.24.0 installed)

Noted that the wlan information for mac is use airport. Default version is Current. (but may be version "A")

## Usage
Enter your HERE API key, which you can get from https://developer.here.com
And execute
```bash=
python get_location.py
```
It will save your wlan log (default file path is ./positioning_result_log.txt) like following
```bash
2021_04_24_15_41_16	{"wlan":[{"mac":"02:1d:aa:18:68:f0","powrx":-76},{"mac":"00:16:16:2a:67:46","powrx":-77},{"mac...
...
```

Also, it will create a Image to show the area around.For example:
![get_geolocation/here_network_positioning_result_2021_04_24_15_41_48.jpg](https://raw.githubusercontent.com/moonstarsky37/get_geolocation/master/here_network_positioning_result_2021_04_24_15_41_48.jpg)
