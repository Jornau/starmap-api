from flask import Flask, jsonify
from flask.json import JSONEncoder
from astro.starmap import Viewpoint, CustomJSONEncoder, Star
from datetime import datetime
from sqlalchemy.ext.declarative import DeclarativeMeta

app = Flask(__name__)

#app.json_encoder = CustomJSONEncoder
class x:
    def __init__(self, x, y):
        self.a = x
        self.b = y

@app.route('/')
def index():
    view = Viewpoint(55, 37, datetime(2019, 2, 28, 19, 10), 3)
    stars = view.visible_stars_now()
    cons = set([x.con_ent.name_eng for x in stars])
    res = {}
    res['constellations'] = list(cons)
    return jsonify(res)


if __name__ == '__main__':
    app.run()