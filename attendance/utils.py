from geopy.distance import geodesic

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points in meters
    using the Haversine formula via the geopy library
    """
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    
    # Calculate distance in meters
    distance = geodesic(point1, point2).meters
    return distance
