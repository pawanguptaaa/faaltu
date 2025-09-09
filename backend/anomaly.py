import time
import math

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points using Haversine formula. Returns distance in km."""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def deviation_from_route(current: tuple, planned_points: list, threshold_km: float = 3.0) -> bool:
    """Return True if current (lat,lng) is > threshold_km away from every planned route point."""
    if not planned_points:
        return False
    lat, lng = current
    for p in planned_points:
        d = calculate_distance(lat, lng, p["lat"], p["lng"])
        if d <= threshold_km:
            return False
    return True

def inactivity(last_update_ts: float, now_ts: float = None, max_idle_minutes: float = 30.0) -> bool:
    now_ts = now_ts or time.time()
    idle_min = (now_ts - last_update_ts) / 60.0
    return idle_min >= max_idle_minutes
