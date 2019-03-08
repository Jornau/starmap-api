from datetime import datetime, timedelta
import math as m

def to_hours(deg: float):
    return(deg * 24) / 360

def equinox_datetime(datetime_now: datetime):
    if datetime_now.month <= 3:
        if datetime_now.month == 3 and datetime_now.day >= 20 and datetime_now.hour >= 12:
            return datetime(datetime_now.year, 3, 20, 12)
        return datetime(datetime_now.year - 1, 3, 20, 12)
    else:
        return datetime(datetime_now.year, 3, 20, 12)

def utc_datetime(datetime_now: datetime, timezone: int):
    return datetime_now - timedelta(hours=timezone)

def delta_to_degrees(dt: timedelta, longitude):
    days = dt.days
    days_deg = days_to_degrees(days)
    time_deg = sec_to_degrees((dt - timedelta(days=days)).total_seconds()) + longitude
    total_deg = days_deg + time_deg
    add_days = total_deg // 360
    total_deg = total_deg - 360 * add_days - days_to_degrees(add_days)
    
    return total_deg

def days_to_degrees(days):
    return days * 360 / 365.242199

def sec_to_degrees(sec):
    return sec / 3600 * 15

def ra_dec_to_az_alt(ra, dec, latitude, degrees_gone):
    _lat = m.radians(latitude)
    _dec = m.radians(dec)
    _ra = ra * 15
    _ha = m.radians(degrees_gone - _ra)
    alt = (m.sin(_dec)*m.sin(_lat) + m.cos(_dec)*m.cos(_lat)*m.cos(_ha))
    az = ((m.sin(_dec) - alt*m.sin(_lat)) / (m.cos(m.asin(alt))*m.cos(_lat)))
    alt = m.degrees(m.asin(alt))
    if m.sin(_ha) < 0:
        az = m.degrees(m.acos(az))
    else:
        az = 360 - m.degrees(m.acos(az))
    return alt, az