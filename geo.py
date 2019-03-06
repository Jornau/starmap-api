import requests as r
import json
import re

class Geo(object):

    def __init__(self, city):
        res = r.get(f'http://api.geonames.org/searchJSON?name_equals={city}&username=Jornau&style=full')
        if (res.status_code != 200):
            raise Exception('Failed to get geo information.')

        tz_pattern = (r'(?<=\"timeZoneId\":\").+?(?=\")')
        gmt_pattern = (r'(?<=\"gmtOffset\":).+?(?=\,)')
        dst_pattern = (r'(?<=\"dstOffset\":).+?(?=\})')
        lat_pattern = (r'(?<=\"lat\":\").+?(?=\")')
        lon_pattern = (r'(?<=\"lng\":\").+?(?=\")')
        
        tz = re.findall(tz_pattern, res.text)        
        gmt = re.findall(gmt_pattern, res.text)
        dst = re.findall(dst_pattern, res.text)
        lat = re.findall(lat_pattern, res.text)
        lon = re.findall(lon_pattern, res.text)
        
        self.gmt = gmt[0]
        self.timezone = tz[0]
        self.dst = dst[0]
        self.lat = float(lat[0])
        self.lon = float(lon[0])
        self.city = city
        