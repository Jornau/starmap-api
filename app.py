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

        user_geo = req.get_entities(pyalice.YA_GEO)
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

        user_datetime = req.get_entities(pyalice.YA_DT)
        if len(user_datetime) > 0:
            dt_loc, offset = user_datetime[0].get_datetime(cur_user.timezone)
        tz = pytz.timezone(cur_user.timezone)
        dt_loc = datetime.now(tz)
        cons = get_constellation(cur_user.lat, cur_user.lon, dt_loc, 10)
        r = str.join('\n', cons)
        return f'{r}'


    return cur_user.timezone


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

def get_constellation(latitude, longitude, dt, lim):
    view = Viewpoint(latitude, longitude, dt)
    return list(set([x.con_ent.name_rus for x in view.visible_cons_now(60)]))[:lim]

if __name__ == '__main__':
    app.run()