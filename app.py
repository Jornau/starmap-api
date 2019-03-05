from flask import Flask, jsonify, request
from astro.starmap import Viewpoint, CustomJSONEncoder, Star
from datetime import datetime
from sqlalchemy.ext.declarative import DeclarativeMeta
import json
import pyalice
import time
TOKEN = 'AQAAAAAntjk7AAT7o_0zkdk7VEsqtM2-PfkNR44'
ID = '556d8e12-1127-4c16-9fe1-bc4c9bd61df1'
app = Flask(__name__)

@app.route('/api', methods=['POST'])
def index():
    z = pyalice.Request(request.json)
    print(z.request.markup[0])
    print(len(z.request.markup))
    for i in z.request.markup:
        print(i)
    payl = {'obj': 2, 'objs': 32}
    v = pyalice.Response(z, 'Привет, чувак!', 'Произношение').add_items_card()\
        .add_image(title='asd').add_image_button('Кнопа', payload=payl).add_header('Это наша галерея')\
            .add_footer('Ha-Ha').add_footer_button('Еще кнопка в подвале')\
                .add_button('TTest').add_button('TTest2', 'http://', payload=payl)
    return v.build_json()


if __name__ == '__main__':
    app.run()