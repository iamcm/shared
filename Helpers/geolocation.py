import math

def distance_between(lat1, lng1, lat2, lng2):
    """
    args: lat1, lng1, lat2, lng2
    Returns the distance between two geolocations in metres 
    """
    lat1 = float(lat1)
    lng1 = float(lng1)
    lat2 = float(lat2)
    lng2 = float(lng2)
    earthradius = float(6371) # Radius of the earth in km
    dlat = _deg2rad(lat2-lat1)
    dlng = _deg2rad(lng2-lng1); 
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(_deg2rad(lat1)) * math.cos(_deg2rad(lat2)) * math.sin(dlng/2) * math.sin(dlng/2)
     
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)); 
    d = (earthradius * c) * 1000 # Distance in m
    return d

def _deg2rad(deg) :
    return float(deg * (math.pi/180))

def bearing(from_x, from_y, to_x, to_y):
    from_x = float(from_x)
    from_y = float(from_y)
    to_x = float(to_x)
    to_y = float(to_y)
    angle = math.degrees(math.atan2(to_y - from_y, to_x - from_x))
    return (angle + 360) % 360