from __future__ import unicode_literals
from flask import Flask, jsonify, request
from starmap import Viewpoint
from datetime import datetime
import json
import pyalice

TOKEN = 'AQAAAAAntjk7AAT7o_0zkdk7VEsqtM2-PfkNR44'
ID = '556d8e12-1127-4c16-9fe1-bc4c9bd61df1'
d = 'Сегодня ночью будут'
app = Flask(__name__)

@app.route('/api', methods=['POST'])
def main():
    req = pyalice.Request(request.json)
    res = pyalice.Response(req, None)
    if 'созвезди' and 'ноч' in req.request.command:
        cons = get_constellation()
        res.response = constellations_card(cons, 'Сегодня ночью будут')
        return res.build_json()
    elif 'созвезди' and 'сейчас' in req.request.command:
        cons = get_constellation()
        res.response = constellations_card(cons, 'Сейчас')
        return res.build_json()

    if req.session.new == True:
        res.response.text = 'Привет! Я пока только учусь, но уже могу подсказать какие созведия в зените сейчас или будут сегодня ночью.'
        res.add_button('Созвездия сейчас').add_button('Созвездия ночью')
        return res.build_json()

    res.response.text = 'Во как! Возьми подсказку зала.'
    res.add_button('Созвездия сейчас').add_button('Созвездия ночью')
    return res.build_json()

def constellations_card(cons, phrase):    
    text = f'{phrase} в зените следующие созвездия:\n{str.join(", ", cons)}'
    response = pyalice.ResponseBody(text, None, None, None, True)
    return response

def get_constellation():
    view = Viewpoint(55, 37, datetime.now(), 3)
    return list(set([x.con_ent.name_rus for x in view.visible_stars_now() if x.alt > 60]))

if __name__ == '__main__':
    app.run()