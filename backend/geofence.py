from shapely.geometry import Point, Polygon

# Example high-risk polygon (dummy coords around a region)
HIGH_RISK_POLYGONS = [
    Polygon([
        (91.73, 26.14),
        (91.80, 26.14),
        (91.80, 26.20),
        (91.73, 26.20),
        (91.73, 26.14),
    ]),
]

def in_high_risk_zone(lat: float, lng: float) -> bool:
    p = Point(lng, lat)  # shapely uses (x=lng, y=lat)
    return any(poly.contains(p) for poly in HIGH_RISK_POLYGONS)
