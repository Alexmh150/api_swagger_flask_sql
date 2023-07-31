import math

# Calculate the distance using haversine formula
def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    a = math.sin(d_lat/2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    radius = 6371 
    distance = radius * c

    return distance

# Extract lat and long from string point
def extract_lat_long_from_point(point_string):
    point_string = point_string.replace("POINT ", "").replace("(", "").replace(")", "")

    # Split the string into latitude and longitude parts
    lat, lon = point_string.split()

    # Convert latitude and longitude to float
    lat = float(lat)
    lon = float(lon)

    return lat, lon

# Calculate the distance from coordinates
def calculate_distance(origin_coord, destination_coord):
    lat1, lon1 = extract_lat_long_from_point(origin_coord)
    lat2, lon2 = extract_lat_long_from_point(destination_coord)
    
    distance = haversine_distance(lat1, lon1, lat2, lon2)

    return distance