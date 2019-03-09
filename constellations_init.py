from sqlalchemy import create_engine, Column, Integer, DateTime, String, Float, ForeignKey, update
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from converter import to_hours

engine = create_engine('sqlite:///db/stars.db')
Base = declarative_base()


class Country(Base):
    __tablename__ = 'Countries'

    id = Column(Integer, primary_key=True)
    full_name_rus = Column(String(100))
    name_rus = Column(String(100))
    full_name_eng = Column(String(100))
    name_eng = Column(String(100))
    iso_num = Column(Integer)
    iso_two = Column(String(2))
    iso_three = Column(String(3))

    def __init__(self, full_name_rus, name_rus, full_name_eng, name_eng, iso_num, iso_two, iso_three):
        self.full_name_rus = full_name_rus
        self.name_rus = name_rus
        self.full_name_eng = full_name_eng
        self.name_eng = name_eng
        self.iso_num = iso_num
        self.iso_two = iso_two
        self.iso_three = iso_three

class City(Base):
    __tablename__ = 'Cities'

    id = Column(Integer, primary_key=True)
    geo_id = Column(Integer)
    name_utf = Column(String(200))
    name_ascii = Column(String(200))
    lat = Column(Float)
    lon = Column(Float)
    country_id = Column(Integer, ForeignKey('Countries.id'))
    country = relationship('Country', foreign_keys=country_id)
    timezone = Column(String(40))

    def __init__(self, geo_id, name_utf, name_ascii, lat, lon, country_id, timezone):
        self.geo_id = geo_id
        self.name_utf = name_utf
        self.name_ascii = name_ascii
        self.lat = lat
        self.lon = lon
        self.country_id = country_id
        self.timezone = timezone

class AltName(Base):
    __tablename__ = 'AltNames'

    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    city_id = Column(Integer,ForeignKey('Cities.id'))
    city = relationship('City', lazy='joined', foreign_keys=city_id)

    def __init__(self, name, city):
        self.name = name
        self.city = city

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), unique=True)
    city = Column(String(50), nullable=True)
    city_last = Column(String(50), nullable=True)
    lat = Column(Float, nullable=True)
    lat_last = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    lon_last = Column(Float, nullable=True)
    dt_last = Column(String(100), nullable=True)
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

#Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

Session = sessionmaker(bind=engine)
session = Session()
#User.__table__.create(session.bind)
#Country.__table__.create(session.bind)
#City.__table__.create(session.bind)
#AltName.__table__.create(session.bind)
print(session.query(User.lon_last).filter(User.user_id == 'alsur6d_13_4').one())
""" def add_column(engine, table_name, column):
    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    engine.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type))

add_column(engine, 'Users',Column('city_last', String(50))) """


""" import io
wr = io.open('C:/VSprojects/Startups/Stars/_stars/res.txt', 'w', encoding='utf-8')
for line in io.open('C:/VSprojects/Startups/Stars/_stars/allCountries.txt', encoding='utf-8'):
    z = line.split('\t')
    if z[8] == 'RU' and z[3] != '':
        wr.write(line)
wr.flush()
wr.close() """

""" import io
alt_names = []
i = 0
for line in io.open('C:/VSprojects/Startups/Stars/_stars/res.txt', encoding='utf-8'):
    obj = line.split('\t')
    try:
        obj[3].encode('ascii')
    except UnicodeEncodeError:
        pass
    else:
        continue

    if session.query(City).filter(City.geo_id == int(obj[0])).first() == None:
        obj = list(map(lambda x: x.strip(), obj))
        country_id = 179
        city = City(int(obj[0]), obj[1], obj[2], float(obj[4]), float(obj[5]), country_id, obj[17])
        for alt in obj[3].split(','):
            try:
                alt.encode('ascii')
            except UnicodeEncodeError:
                pass
            else:
                continue
            alt_name = AltName(alt, city)
            alt_names.append(alt_name)
            i +=1
        if i % 1000 == 0:
            session.add_all(alt_names)
            alt_names = []
            print(i)

session.add_all(alt_names) """


""" session.add(Country('Аландские острова', 'Аландские острова', 'Aland Islands', 'Aland Islands', 248, 'AX', 'ALA'))
session.add(Country('Сен-Бартелеми', 'Сен-Барт', 'Saint Barthelemy', 'Saint Barthelemy', 652, 'BL', 'BLM'))
session.add(Country('остров Кюрасао', 'остров Кюрасао', 'Curacao', 'Curacao', 531, 'CW', 'CUW'))
session.add(Country('Черногория', 'Черногория', 'Montenegro', 'Montenegro', 499, 'ME', 'MNE'))
session.add(Country('Сен-Мартен', 'Сен-Мартен', 'Saint-Martin', 'Saint-Martin', 663, 'MF', 'MAF'))
session.add(Country('Сербия', 'Республика Сербия', 'The Republic of Serbia', 'Serbia', 688, 'RS', 'SRB'))
session.add(Country('Южный Судан', 'Южный Судан', 'South Sudan', 'South Sudan', 728, 'SS', 'SSD'))
session.add(Country('Сен-Мартен', 'Сен-Мартен', 'Saint-Martin', 'Saint-Martin', 534, 'SX', 'SXM'))
session.add(Country('Косово', 'Косово', 'Kosovo', 'Kosovo', 383, 'XK', 'SXM'))
session.add(Country('Бонэйр, Синт-Эстатиус и Саба', 'Карибские Нидерланды', 'Bonaire, Saint Eustatius and Saba', 'Bonaire, Saint Eustatius and Saba', -1, 'BQ', 'BES'))
 """
""" import io
alt_names = []
i = 0
for line in io.open('C:/VSprojects/Startups/Stars/_stars/cities500.csv', encoding='utf-8'):
    obj = line.split('\t')

    if (obj[3] != ''):
        try:
            obj[3].encode('ascii')
        except UnicodeEncodeError:
            pass
        else:
            continue
        obj = list(map(lambda x: x.strip(), obj))
        country_id = session.query(Country).filter(Country.iso_two == obj[8]).first()
        if country_id == None:
            print(obj[8])
        country_id = country_id.id
        city = City(int(obj[0]), obj[1], obj[2], float(obj[4]), float(obj[5]), country_id, obj[17])
        for alt in obj[3].split(','):
            try:
                alt.encode('ascii')
            except UnicodeEncodeError:
                pass
            else:
                continue
            alt_name = AltName(alt, city)
            alt_names.append(alt_name)
            i +=1
    if i % 1000 == 0:
        session.add_all(alt_names)
        alt_names = []

session.add_all(alt_names)
z = session.query(AltName).count()
b = session.query(City).count()
session.commit()
print(z)
print(b)
print(session.query(City).first().timezone) """

""" countries = []
for line in open('C:/VSprojects/Startups/Stars/_stars/countries.csv', 'r'):
    obj = line.split(';')
    map(lambda x: x.strip(), obj)
    country = Country(obj[1], obj[2], obj[3], obj[4], int(obj[5]), obj[6], obj[7])
    countries.append(country)

session.add_all(countries)
session.commit() """
try:
    'Эл Тартер'.encode('ascii')
except UnicodeEncodeError:
    print("it was not a ascii-encoded unicode string")
else:
    print("It may have been an ascii-encoded unicode string")

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
import pytz
tz = pytz.timezone('Europe/Moscow')
view = Viewpoint(55, 37, datetime(2019, 2, 28, 19, 10, tzinfo=tz))
print('UTC:', view.utc_datetime_now)
print('Local', view.datetime_now)
print('Eq_date', view.start_point)
print(view.degrees_gone)
z = to_hours(view.degrees_gone)
zm = (z - int(z)) * 60
print('Cur Eq', int(z), int(zm))

c = view.visible_cons_now(0)
print(c)
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
plt.show()
 """
import pytz

#utc_dt = datetime.now().replace(tzinfo=pytz.UTC)

utc_dt = datetime.utcnow()
timezone = pytz.timezone('Europe/Moscow')
loc_dt = timezone.utcoffset(utc_dt)


