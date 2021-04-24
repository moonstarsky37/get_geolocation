import os, platform, subprocess
import plistlib
import re, json
import time
import requests

def get_mac_list():
    if platform.system() == 'Windows':
        results = subprocess.check_output(["netsh", "wlan", "show", "network", "bssid"])
        results = results.decode("ascii", errors='ignore')  # needed in python 3
        results_list = results.replace('\r', '').replace('    ', '').split('\n\n')
        i = 0
        parsed_result_list = []
        for results in results_list:
            results = results.split('\n')
            for result in results:
                if result.startswith('BSSID') or result.startswith(' Signal'):
                    parsed_result_list.append(result.split(' : ')[1].strip())
                else:
                    continue
        mac_list = set()
        while i < len(parsed_result_list):
            if i % 2 == 1:
                signal_percentage = int(parsed_result_list[i].replace('%', ''))
                mac_list.add('{"mac": "' + parsed_result_list[i - 1] + '", "powrx": ' + str(int((signal_percentage / 2) - 100)) + '}')
            i += 1
    elif platform.system() == 'Darwin':
        command = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s -x'  # Current or A
        process = subprocess.Popen(command, 
                                    stdout=subprocess.PIPE, 
                                    stderr=None, 
                                    shell=True)
        output = process.communicate()
        output = output[0].decode('utf-8', errors='ignore')
        hotspots_plist = plistlib.loads(str.encode(output), 
                                        fmt=plistlib.FMT_XML)
        mac_list = set()
        for hotspot in hotspots_plist:
            ssid_str = hotspot['SSID_STR']
            bssid = hotspot['BSSID']
            rssi = hotspot['RSSI']
            if not re.findall('\w\w:'*5+'\w\w', hotspot['BSSID']):
                bssid_arr = bssid.split(':')
                bssid_modified_arr = []
                for bssid_elem in bssid_arr:
                    if len(bssid_elem) == 1:
                        bssid_elem = '0{}'.format(bssid_elem)
                    bssid_modified_arr.append(bssid_elem)
                bssid = ':'.join(bssid_modified_arr)
            line = '{\"mac\":\"'+bssid+'\",\"powrx\":'+str(rssi)+'}'
            mac_list.add(line)  # BSSID + Powrx
    return mac_list

def rev_geocoder(lat, lon):
    rev_geocoder_url = 'https://revgeocode.search.hereapi.com/v1/revgeocode?at={},{}&limit=10&lang=zh-TW&apikey={}'.format(
        lat, lon, api_key)
    r = requests.get(rev_geocoder_url)
    rev_geocoder_result_items = json.loads(r.text).get('items')
    for rev_geocoder_result_item in rev_geocoder_result_items:
        result_type = rev_geocoder_result_item['resultType']
        if result_type == 'houseNumber' or result_type == 'street' or result_type == 'intersection':
            result_position = rev_geocoder_result_item['position']
            result_lat = result_position['lat']
            result_lon = result_position['lng']
            result_title = rev_geocoder_result_item['title']
            return (result_lat, result_lon, result_title)
        else:
            continue

def mia_cicular_picture(lon, lat, radius, label,
                        log_text,
                        log_file_name='positioning_result_log.txt', 
                        image_folder="./"):
    mia_url = 'https://image.maps.ls.hereapi.com/mia/1.6/mapview'
    mia_url = '{}?c={},{}&u={}&w=1440&h=900&ml=cht' \
              '&ppi=250&apiKey={}&t=3&tx={},{};{}&txs=30'.format(mia_url, 
              lat, lon, radius, api_key, lat - 0.00005, lon, label)
    image_data = requests.get(mia_url).content
    timestamp = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
    image_file_name = 'here_network_positioning_result_{}.jpg'.format(timestamp)
    image_file_name = os.path.join(image_folder, image_file_name)
    with open(log_file_name, mode='a', encoding='utf-8') as f:
        f.write('{}\t{}\t{}\t{}\n'.format(timestamp, 
                                        wifi_scan_result,  
                                        log_text, 
                                        label))
    with open(image_file_name, 'wb') as handler:
        handler.write(image_data)

def wifi_scan_fmt(mac_list):
    return '{"wlan":[' + ','.join(i for i in mac_list) + ']}'

def get_posision_by_hereAPI(api_key, wifi_scan_result):
    positioning_headers = {'Content-Type': 'application/json'}
    positioning_url = 'https://pos.ls.hereapi.com/positioning/v1/locate'
    positioning_url += '?apiKey={}'.format(api_key)
    r, parsing_status = None, 404
    if len(mac_list)!=0:
        r = requests.post(url=positioning_url, 
                                            data=wifi_scan_result, 
                                            headers=positioning_headers)
        parsing_status = r.status_code
    return r, parsing_status  

if __name__ == '__main__':
    api_key = '<YOUR HERE API KEY>'  # YOUR HERE API KEY from HERE
    mac_list = get_mac_list()
    wifi_scan_result = wifi_scan_fmt(mac_list)
    print('Wifi hotspots:\n' + wifi_scan_result)
    pos_r, status_c = get_posision_by_hereAPI(api_key, wifi_scan_result)

    if status_c == 200:
        json_result = json.loads(network_positioning_r.text)
        lat = json_result['location']['lat']
        lon = json_result['location']['lng']
        radius = json_result['location']['accuracy']     
    else:
        print("'wlan' must contain at least 1 items\n Use ip detect location")
        _ip = requests.get("https://ipinfo.io/ip").text
        print("Your IP is {}".format(_ip))
        try:
            latlon = requests.get("https://ipinfo.io/loc").text
            lat, lon = latlon.replace("\n", "").split(",")
            lat, lon = float(lat), float(lon)
            radius = 50
            json_result = dict()
            json_result["location"] = {'lat': lat, 'lng': lon, 
                                        'accuracy': radius}
        except ImportError as e:
            print("No internet connection found.")
            pass  
    print('result:\n' + str(json_result))
    address_lat, address_lon, address_label = rev_geocoder(lat, lon)
    mia_cicular_picture(lon, lat, radius, address_label, json_result)
