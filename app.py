from __future__ import unicode_literals
from flask import Flask, jsonify, request
from starmap import Viewpoint, User, DB
from datetime import datetime
import geo, pytz, pyalice, json

TOKEN = 'AQAAAAAntjk7AAT7o_0zkdk7VEsqtM2-PfkNR44'
ID = '556d8e12-1127-4c16-9fe1-bc4c9bd61df1'

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def main():
    req = pyalice.In(request.json)
    res = pyalice.Out(req)
    user_id = req.session.user_id

    db = DB()
    cur_user = db.get_user(user_id)
    if cur_user == None:
        cur_user = db.add_user(user_id)
    db.close()

    if 'созвезди' in req.request.command:
        user_geo = [x for x in req.request.nlu.entities if x.type == 'YANDEX.GEO']
        if len(user_geo) > 0 and user_geo[0].value.city != None:
            try:
                n_geo = geo.Geo(user_geo[0].value.city)
            except:
                return 'НЕ ПОЛУЧИЛОСЬ ОПРЕДЕЛИТЬ МЕСТОПОЛОЖЕНИЕ!'
            cur_user.timezone = n_geo.timezone
            cur_user.city = n_geo.city
            cur_user.lat = n_geo.lat
            cur_user.lon = n_geo.lon
        if cur_user.timezone == None:
            return 'УКАЖИТЕ МЕСТО НАБЛЮДЕНИЯ!'
        user_datetime = [x for x in req.request.nlu.entities if x.type == 'YANDEX.DATETIME']

        if len(user_datetime) > 0:
            dt_loc, offset = build_datetime(cur_user.timezone, user_datetime[0].value)
        else:
            dt_loc, offset = build_datetime(cur_user.timezone)
        
        cons = get_constellation(cur_user.lat, cur_user.lon, dt_loc, offset, 5)
        r = str.join('\n', cons)
        return f'{r}'


    return cur_user.timezone

def build_datetime(tz, a_dt = None):
    dt_utc = datetime.utcnow()
    timezone = pytz.timezone(tz)
    dt = dt_utc.astimezone(timezone)
    if a_dt != None:
        year = convert_date(dt.year, a_dt.year, a_dt.year_is_relative)
        month = convert_date(dt.month, a_dt.month, a_dt.month_is_relative)
        day = convert_date(dt.day, a_dt.day, a_dt.day_is_relative)
        hour = convert_date(0, a_dt.hour, a_dt.hour_is_relative)
        minute = convert_date(0, a_dt.minute, a_dt.minute_is_relative)
        dt_user = datetime(year, month, day, hour, minute)
    else:
        dt_user = dt.replace(hour=23)

    offset_delta = timezone.utcoffset(dt_utc)
    offset = int(offset_delta.total_seconds() / 3600)
    return dt_user, offset

def convert_date(cur, val, relative):
    if relative == None:
        return cur
    elif relative == False:
        return val
    else:
        return cur #+ val

def constellations_card(phrase, cons, cur_user, dt_loc):    
    text = f'{phrase} в зените следующие созвездия:\n{str.join(", ", cons)}'
    
    pl = {
        'lat': cur_user.lat,
        'lon': cur_user.lon,
        'dt_loc': f'{dt_loc}',
        'offset': cur_user.offset,
        'lim': 100,
    }
    btn = pyalice.TipButton('Полный список', None, pl, True)
    r = pyalice.Response(text, text, buttons=[btn])
    return r

def get_constellation(latitude, longitude, dt, timezone, lim):
    view = Viewpoint(latitude, longitude, dt, timezone)
    return list(set([x.con_ent.name_rus for x in view.visible_stars_now() if x.alt > 60]))[:lim]

if __name__ == '__main__':
    app.run()