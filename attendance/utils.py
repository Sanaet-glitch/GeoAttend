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

def verify_location(student_location, class_location, allowed_radius):
    """
    Verify if student's location is within the allowed radius of the class location
    
    Parameters:
    - student_location: tuple of (latitude, longitude)
    - class_location: tuple of (latitude, longitude)
    - allowed_radius: radius in meters
    
    Returns:
    - Dictionary with verification results
    """
    distance = calculate_distance(
        student_location[0],
        student_location[1],
        class_location[0],
        class_location[1]
    )
    
    return {
        'is_within_radius': distance <= allowed_radius,
        'distance': distance,
        'allowed_radius': allowed_radius
    }
