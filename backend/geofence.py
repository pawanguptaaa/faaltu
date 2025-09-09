# Simple geofencing without shapely dependency
# Example high-risk zones (bounding box format: [min_lng, min_lat, max_lng, max_lat])
HIGH_RISK_ZONES = [
    [91.73, 26.14, 91.80, 26.20],  # Example high-risk area
]

def in_high_risk_zone(lat: float, lng: float) -> bool:
    """Check if coordinates are within any high-risk zone using simple bounding box."""
    for zone in HIGH_RISK_ZONES:
        min_lng, min_lat, max_lng, max_lat = zone
        if min_lng <= lng <= max_lng and min_lat <= lat <= max_lat:
            return True
    return False
