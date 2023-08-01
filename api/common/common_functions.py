import math

# pagination
def paginate_query_result(query_result, page=1, per_page=10):
    total_items = query_result.count()  # Get the total number of items in the query result
    total_pages = (total_items + per_page - 1) // per_page  # Calculate the total number of pages
    offset = (page - 1) * per_page  # Calculate the offset for pagination
    query_paginated = query_result.offset(offset).limit(per_page)  # Get the paginated data

    # Return the paginated data along with pagination information
    response = {
        'total_items': total_items,
        'total_pages': total_pages,
        'current_page': page
    }

    return response, query_paginated

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