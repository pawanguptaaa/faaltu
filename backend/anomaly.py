from geopy.distance import geodesic
import time

def deviation_from_route(current: tuple, planned_points: list, threshold_km: float = 3.0) -> bool:
    """Return True if current (lat,lng) is > threshold_km away from every planned route point."""
    if not planned_points:
        return False
    lat, lng = current
    for p in planned_points:
        d = geodesic((lat, lng), (p["lat"], p["lng"])).km
        if d <= threshold_km:
            return False
    return True

def inactivity(last_update_ts: float, now_ts: float = None, max_idle_minutes: float = 30.0) -> bool:
    now_ts = now_ts or time.time()
    idle_min = (now_ts - last_update_ts) / 60.0
    return idle_min >= max_idle_minutes
