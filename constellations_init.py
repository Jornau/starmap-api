from sqlalchemy import create_engine, Column, Integer, DateTime, String, Float, ForeignKey, update
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from converter import to_hours

engine = create_engine('sqlite:///db/stars.db')
Base = declarative_base()

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), unique=True)
    city = Column(String(50), nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    gmt = Column(Integer, nullable=True)
    dst = Column(Integer, nullable=True)
    timezone = Column(String(50), nullable=True)


class Constellation(Base):

    __tablename__ = "Constellations"

    id = Column(Integer, primary_key=True)
    name_eng = Column(String(50))
    name_rus = Column(String(50))
    abbr_iau = Column(String(5))
    abbr_nasa = Column(String(5))
    area = Column(Integer)

    def __init__(self, name_eng, name_rus, abbr_iau, abbr_nasa, area):
        self.name_eng = name_eng 
        self.name_rus = name_rus 
        self.abbr_iau = abbr_iau 
        self.abbr_nasa = abbr_nasa 
        self.area = area 

    def __repr__(self):
        return "<Constellation('%s','%s', '%s', '%s', '%s')>" % (self.name_eng, self.name_rus, self.abbr_iau, self.abbr_nasa, self.area)

class Star(Base):

    __tablename__ = "Stars"

    id = Column(Integer, primary_key=True)
    hip = Column(Integer, nullable=True)
    hd = Column(Integer, nullable=True)
    hr = Column(Integer, nullable=True)
    flam = Column(Integer, nullable=True)
    gl = Column(String(30), nullable=True)
    bf = Column(String(30), nullable=True)
    spect = Column(String(30), nullable=True)
    bayer = Column(String(30), nullable=True)
    var = Column(String(30), nullable=True)
    name_eng = Column(String(50), nullable=True)
    name_rus = Column(String(50), nullable=True)
    ra = Column(Float)
    dec = Column(Float)
    dist = Column(Float)
    pmra = Column(Float)
    pmdec = Column(Float)
    mag = Column(Float)
    absmag = Column(Float)
    lum = Column(Float)
    rv = Column(Float, nullable=True)
    ci = Column(Float, nullable=True)
    con = Column(Integer, ForeignKey('Constellations.id'), nullable=True)
    con_ent = relationship("Constellation", foreign_keys=con)

    def __init__(self, ra, dec, dist, pmra, pmdec, mag, absmag, lum, hip = None, hd = None, hr = None, gl = None, bf = None,
        name_eng = None, name_rus = None, rv = None, spect = None, ci = None, bayer = None, flam = None, con = None,var = None):
        self.ra = ra 
        self.dec = dec 
        self.dist = dist 
        self.pmra = pmra 
        self.pmdec = pmdec
        self.mag = mag
        self.absmag = absmag
        self.hip = hip
        self.hd = hd
        self.hr = hr
        self.gl = gl
        self.bf = bf
        self.name_eng = name_eng
        self.name_rus = name_rus
        self.rv = rv
        self.spect = spect
        self.ci = ci
        self.bayer = bayer
        self.flam = flam
        self.con = con
        self.var = var
        self.lum = lum

Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

Session = sessionmaker(bind=engine)
session = Session()
#User.__table__.create(session.bind)


""" cons = []
for line in open('_stars/cons.csv'):
    obj = obj = line.strip().split(';')
    con = Constellation(obj[1], obj[0], obj[2], obj[3], obj[4])
    cons.append(con)

session.add_all(cons)
session.commit()
 """
"""_csv = open('_stars/hygdata_v3.csv','r')
cons = session.query(Constellation).all()
_csv.readline()
stars = []
for line in _csv:
    obj = line.strip().split(',')
    if (float(obj[13]) <= 6.0):

        if (obj[16] == ''):
            obj[16] = None

        if (obj[29] != ''):
            obj[29] = session.query(Constellation.id).filter(func.upper(Constellation.abbr_iau) == func.upper(obj[29])).one()[0]
        else:
            obj[29] = None

        star = Star(obj[7], obj[8], obj[9], obj[10], obj[11], obj[13], obj[14], obj[33], obj[1], obj[2],
            obj[3], obj[4], obj[5], obj[6], None, obj[12], obj[15], obj[16], obj[27], obj[28], obj[29], obj[34])
        stars.append(star)
session.add_all(stars)
session.commit()
session.close()
"""



""" from starmap import Viewpoint

view = Viewpoint(55, 37, datetime(2019, 2, 28, 19, 10), 3)
print('UTC:', view.utc_datetime_now)
print('Local', view.datetime_now)
print('Eq_date', view.start_point)
print(view.degrees_gone)
z = to_hours(view.degrees_gone)
zm = (z - int(z)) * 60
print('Cur Eq', int(z), int(zm))

c = view.visible_stars_now()

import matplotlib.pyplot as plt
c = [x for x in c if x.mag < 5]
decs = [x.alt for x in c]
ras = [x.az for x in c]
siz = [6*10 - x.mag*10 for x in c]
names = [x.con_ent.name_eng for x in c]
fig = plt.figure(figsize=[10,10])
fig.suptitle('Star Sky')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.scatter(ras, decs, marker='o', c='r', s=siz)
#plt.gca().invert_xaxis()
for i, txt in enumerate(names):
    if txt != '':
        plt.text(ras[i], decs[i], txt)
plt.show() """

import pytz

#utc_dt = datetime.now().replace(tzinfo=pytz.UTC)

utc_dt = datetime.utcnow()
utc_dt += timedelta(days=50)
timezone = pytz.timezone('Europe/Moscow')
loc_dt = timezone.utcoffset(utc_dt)
print(utc_dt)
print(int(loc_dt.total_seconds() / 3600))

