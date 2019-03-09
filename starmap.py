from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, or_, and_, MetaData, func
from sqlalchemy.orm import sessionmaker, relationship
from converter import to_hours, equinox_datetime, utc_datetime, delta_to_degrees, ra_dec_to_az_alt
from datetime import datetime
import math as m
from flask import jsonify
from flask.json import JSONEncoder
import json
import os.path as p

Base = declarative_base()

DB_CON = 'sqlite:///db/stars.db' #'sqlite:////home/jornau/starmap-api/db/stars.db' #'sqlite:///db/stars.db'
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
    con_ent = relationship("Constellation", lazy='joined', foreign_keys=con)

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

class Viewpoint(object):
    
    def __init__(self, latitude, longitude, datetime_now: datetime):
        
        self.__engine = create_engine(DB_CON)
        self.__session = sessionmaker(bind=self.__engine)()
        self.latitude = latitude
        self.longitude = longitude
        self.datetime_now = datetime_now
        self.timezone = datetime_now.utcoffset().total_seconds() / 3600
        self.utc_datetime_now = utc_datetime(datetime_now.replace(tzinfo=None), self.timezone)
        self.start_point = equinox_datetime(self.utc_datetime_now)
        self.delta_dt = self.utc_datetime_now - self.start_point
        self.degrees_gone = delta_to_degrees(self.delta_dt, self.longitude)

    def __repr__(self):
        return "<Viewport('%d','%d')" % (self.latitude, self.longitude)

    def visible_cons_now(self, min_):
        stars = []
        for star in self.__session.query(Star).filter(Star.con != None).all():
            alt, az = ra_dec_to_az_alt(star.ra, star.dec, self.latitude, self.degrees_gone)
            if star.con_ent.name_rus not in stars and alt > min_:
                star.alt = alt
                star.az = az
                stars.append(star.con_ent.name_rus)
        self.close()
        return stars

    def close(self):
        self.__session.close()
        self.__engine.dispose()
    
class DB(object):
    def __init__(self):
        self.__engine = create_engine(DB_CON)
        self.__session = sessionmaker(bind=self.__engine, autoflush=False)()

    def get_user(self, user_id):
        return self.__session.query(User).filter(User.user_id == user_id).first()

    def get_geo(self, city):
        return self.__session.query(AltName).filter(AltName.name == city).first()

    def add_user(self, user_id):
        user = User(user_id = user_id)
        self.__session.add(user)
        self.__session.commit()
        return user

    def seession_rollback(self):
        self.__session.rollback()

    def update_user(self, user):
        self.__session.add(user)
        self.__session.commit()    

    def close(self):
        self.__session.close()
        self.__engine.dispose()

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

