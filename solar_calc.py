import math
from datetime import datetime, timezone

def calculate_sun_position(utc_time, lat, lon):
    jd = utc_time.toordinal() + 1721425 + (utc_time.hour + utc_time.minute / 60.0) / 24.0
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lambda_sun = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    epsilon = math.radians(23.439 - 0.0000004 * n)
    alpha = math.atan2(math.cos(epsilon) * math.sin(lambda_sun), math.cos(lambda_sun))
    delta = math.asin(math.sin(epsilon) * math.sin(lambda_sun))
    lst = (100.46 + 0.98564736 * n + lon + 15 * utc_time.hour + 0.25) % 360
    ha = math.radians(lst - math.degrees(alpha))
    alt = math.asin(
        math.sin(math.radians(lat)) * math.sin(delta) +
        math.cos(math.radians(lat)) * math.cos(delta) * math.cos(ha)
    )
    az = math.atan2(
        -math.sin(ha),
        math.tan(delta) * math.cos(math.radians(lat)) - math.sin(math.radians(lat)) * math.cos(ha)
    )
    return math.degrees(alt), (math.degrees(az) + 360) % 360

def get_current_sun_position():
    LAT = 30.8697   # weidu
    LON = 108.4325  # jindu
    
    utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    return calculate_sun_position(utc_now, LAT, LON) #AI辅助生成：Qwen3-Coder,2026-02-24
