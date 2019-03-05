from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, or_, and_, MetaData
from sqlalchemy.orm import sessionmaker, relationship
from astro.converter import to_hours, equinox_datetime, utc_datetime, delta_to_degrees
from datetime import datetime
import math as m
from flask import jsonify
from flask.json import JSONEncoder
import json
import os.path as p

Base = declarative_base()
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

class Viewpoint:
    
    def __init__(self, latitude, longitude, datetime_now: datetime, timezone):
        
        db = '/home/wwwroot/stars-api/flask-uwsgi/stars.db'
        db2 = 'env/db/stars.db'
        self.__engine = create_engine(f'sqlite:///{db2}')
        self.__session = sessionmaker(bind=self.__engine)()
        self.latitude = latitude
        self.longitude = longitude
        self.datetime_now = datetime_now
        self.timezone = timezone
        self.utc_datetime_now = utc_datetime(datetime_now, timezone)
        self.start_point = equinox_datetime(self.utc_datetime_now)
        self.delta_dt = self.utc_datetime_now - self.start_point
        self.degrees_gone = delta_to_degrees(self.delta_dt, self.longitude)

    def __repr__(self):
        return "<Viewport('%d','%d')" % (self.latitude, self.longitude)

    def visible_stars_now(self):
        stars = []
        for star in self.__session.query(Star).all():
            alt, az = self.__az_at(star.ra, star.dec)
            if alt > 0 and star.con != None:
                star.alt = alt
                star.az = az
                stars.append(star)
        self.close()
        return stars

    def __az_at(self, ra, dec):
        _lat = m.radians(self.latitude)
        _dec = m.radians(dec)
        _ra = ra * 15
        _ha = m.radians(self.degrees_gone - _ra)
        alt = (m.sin(_dec)*m.sin(_lat) + m.cos(_dec)*m.cos(_lat)*m.cos(_ha))
        az = ((m.sin(_dec) - alt*m.sin(_lat)) / (m.cos(m.asin(alt))*m.cos(_lat)))
        alt = m.degrees(m.asin(alt))
        if m.sin(_ha) < 0:
            az = m.degrees(m.acos(az))
        else:
            az = 360 - m.degrees(m.acos(az))
        return alt, az

    def close(self):
        self.__session.close()
        self.__engine.dispose()
    

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):# pylint: disable=E0202
        if isinstance(obj.__class__, DeclarativeMeta):
            return obj.__dict__
        else:
            return json.JSONEncoder.default(self, object)