from __future__ import unicode_literals
from flask import Flask, jsonify, request
from starmap import Viewpoint, User, DB
from datetime import datetime
import geo, pytz, pyalice, json, random

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
    known = True
    if cur_user == None:
        cur_user = db.add_user(user_id)
        known = False


    cmd = req.request.command.lower()

    if 'созвезди' in cmd:

        user_geo = req.get_entities(pyalice.YA_GEO)
        if len(user_geo) > 0 and user_geo[0].value.city != None:
            n_geo = db.get_geo(user_geo[0].value.city)
            if n_geo == None:
                try:
                    n_geo = geo.Geo(user_geo[0].value.city)
                except:
                    if n_geo.status != 200:
                        res.response = tech_problems()
                    else:
                        res.response = ask_loc_again(user_geo[0].value.city)
                    return res.build_json()
                finally:
                    db.close()
            cur_user.timezone = n_geo.timezone
            cur_user.city = n_geo.city
            cur_user.lat = n_geo.lat
            cur_user.lon = n_geo.lon
        if cur_user.timezone == None:
            res.response = ask_location()
            return res.build_json()
        db.close()

        user_datetime = req.get_entities(pyalice.YA_DT)
        if len(user_datetime) > 0:
            dt_loc, offset = user_datetime[0].get_datetime(cur_user.timezone)
        else:
            tzone = pytz.timezone(cur_user.timezone)
            dt_loc = datetime.now(tzone)
            dt_loc = dt_loc.replace(hour=23, minute=00)
        lim = 5 if 'screen' in req.meta.interfaces else 7
        cons = get_constellation(cur_user.lat, cur_user.lon, dt_loc, lim)
        res.response = constellations_card(cons, cur_user, dt_loc)
        return res.build_json()

    if 'показать все' in cmd:
        data = req.request.payload
        if data == None:
            db.close()
            res.response = pyalice.Response('Данная функция доступна только по нажатию кнопки.')
            return res
        cur_user.lat = data['lat']
        cur_user.lon = data['lon']
        dt_loc = datetime.strptime(data['dt_loc'], '%Y-%m-%d %H:%M:%S.%f%z') #2019-03-07 01:25:40.805813+03:00
        lim = data['lim']
        cons = get_constellation(cur_user.lat, cur_user.lon, dt_loc, lim)
        res.response = constellations_card(cons, cur_user, dt_loc, True)
        db.close()
        return res.build_json()

    if 'задать место' in cmd:
        user_geo = req.get_entities(pyalice.YA_GEO)
        if len(user_geo) > 0 and user_geo[0].value.city != None:
            city = user_geo[0].value.city
            n_geo = db.get_geo(city)
            if n_geo == None:
                try:
                    n_geo = geo.Geo(city)
                except:
                    if n_geo.status != 200:
                        res.response = tech_problems()
                    else:
                        res.response = ask_loc_again(city)
                    return res.build_json()
                finally:
                    db.close()
        else:
            res.response = ask_location()
            return res.build_json()

        cur_user.timezone = n_geo.timezone
        cur_user.city = n_geo.city
        cur_user.lat = n_geo.lat
        cur_user.lon = n_geo.lon
        db.update_user(cur_user)
        db.close()
        res.response = confirm_location(city)        
        return res.build_json()

    if 'справка' in cmd:
        res.response = help()
        db.close()
        return res.build_json()

    if req.session.new == True:
        res.response = greeting(cur_user, known)
        db.close()
        return res.build_json()
    
    db.close()
    res.response = no_dialogs()
    return res.build_json()


def constellations_card(cons, cur_user, dt_loc, fl = False):    
    ldt = f'{cur_user.city.title()}. {dt_loc.strftime("%d")} {months[dt_loc.month - 1]} {dt_loc.strftime("%H:%M")}.'
    if len(cons) > 7:
        cons = str.join(", ", cons)
    else:
        cons = str.join("\n", cons)
    if fl == False:
        tts = text = f'{ldt} Созвездия в зените:\n{cons}'
    else:
        tts = text = f'{ldt} Полный список созвездий:\n{cons}'
    pl = {
        'lat': cur_user.lat,
        'lon': cur_user.lon,
        'dt_loc': f'{dt_loc}',
        'lim': 100,
    }
    r = pyalice.Response(text + '\n\n*Время соответствует заданому местоположению.', tts)
    if fl == False:
        r.add_tip_button('Полный список', None, pl, True)
    return r

def get_constellation(latitude, longitude, dt, lim):
    view = Viewpoint(latitude, longitude, dt)
    if lim > 7:
        return view.visible_cons_now(0)[:lim]
    return view.visible_cons_now(65)[:lim]

def greeting(cur_user, known = False):
    text = 'Привет! Я Астроном. Зная дату, время и местоположение, я подскажу какие созвездия можно увидеть. В запросе используйте слово "Созвездия".' +\
        '\n\nПроизнесите команду «Задать местоположение» и назовите населенный пункт. Он будет использоваться по-умолчанию.'+\
        '\n\nДля помощи скажите «Справка»'
    desc = 'Привет! Я Астроном. Зная дату, время и местоположение, я подскажу какие созвездия можно увидеть. В запросе используйте слово "Созвездия".' +\
        '\n\nПроизнесите команду «Задать местоположение» и назовите населенный пункт. Он будет использоваться по-умолчанию.'
    tts = 'Привет! Я Астроном. Зная дату, время и местоположение, я подскажу какие созвездия можно увидеть. В запросе используйте слово "Созвездия".' +\
        '- - - Произнесите команду «Задать местоположение» и назовите населенный пункт. Он будет использоваться по-умолчанию.'+\
        '- - - Для помощи скажите «Справка»'

    text_known = ['Рад, что Вы вернулись.', 'Здравствуйте!', 'Готов начать поиск созвездий.']
    text_known = random.choice(text_known)
    if known == True and cur_user.city != None:
        text = f'{text_known} Сохраненное местоположение - {cur_user.city}.'
    elif known == True and cur_user.city == None:
        tts = text = f'{text_known} Произнесите команду «Задать местоположение» и назовите населенный пункт.'
    r = pyalice.Response(text,tts).add_image_card('1540737/024430afeff32cf0bbd8', description=desc)
    if cur_user.city != None:
        r.add_tip_button('Созвездия сегодня', hide=True)
    r.add_tip_button('Справка', hide=True)
    return r

def no_dialogs():
    chs = ['Такого я не предвидел.', 'Видимо, мы друг друга не поняли.', 'Я просто засмотрелся на звезды.']
    chs = random.choice(chs)
    text = f'{chs} Скажите «Справка», если нужна помощь.'
    return pyalice.Response(text, text).add_tip_button('Справка', hide=True)

def ask_location():
    text = 'Произнесите команду «Задать местоположение» и назовите населенный пункт.'
    return pyalice.Response(text, text).add_tip_button('Созвездия в Москве', hide=True).add_tip_button('Созвездия в Париже', hide=True)

def tech_problems():
    text = 'К сожалению, наш сервис геолокации недоступен. Попробуйте выполнить запрос позднее.'
    return pyalice.Response(text, text)

def ask_loc_again(city):
    text = f'Не удается найти {city}. Если название корректно, попробуйте выбрать другой населенный пункт.'
    return pyalice.Response(text, text)

def confirm_location(city):
    text = f'Местоположение {city.title()} успешно сохранено.'
    return pyalice.Response(text, text).add_tip_button('Созвездия сегодня', hide=True).add_tip_button('Справка', hide=True)

def help():
    text = 'Поисковая фраза должна содержать слово «Созвездия».\n'+\
        'Чтобы задать или изменить место наблюдения, произнесите «Задать местоположение» и назовите населенный пункт.\n'+\
            'Можно указывать место наблюдения прямо в запросе. В таком случае оно не будет сохранено и не заменит место по-умолчанию.\n'+\
                'При отсутствии даты и времени, будут запрошены созвездия на текущую дату в 23:00.'+\
                    'При отсутствии времени - на выбранную дату, тоже в 23:00.'
    tts = 'Поисковая фраза должна содержать слово «Созвездия».'+\
        '- - - Чтобы задать или изменить место наблюдения, произнесите «Задать местоположение» и назовите населенный пункт.'+\
            '- - - Можно указывать место наблюдения прямо в запросе. В таком случае оно не будет сохранено и не заменит место по-умолчанию.'+\
                '- - - При отсутствии даты и времени, будут запрошены созвездия на текущую дату в 23:00.'+\
                    'При отсутствии времени - на выбранную дату, тоже в 23:00.'
    
    return pyalice.Response(text, tts)

months = [
    'января',
    'февраля',
    'марта',
    'апреля',
    'мая',
    'июня',
    'июля',
    'августа',
    'сентября',
    'октября',
    'ноября',
    'декабря'
]

if __name__ == '__main__':
    app.run()