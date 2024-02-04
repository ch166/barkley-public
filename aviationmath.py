#
# aviationmath.py
#

"""
Set of basic utility functions that return aviation useful answers
"""

import math


def knot2mph(knots):
    """
    Converts knots to miles per hour.
    Nautical Mile is now defined as a Meters value
    Nautical Mile = 1852m
    Statute Mile = 5280 ft
    """
    if knots is None:
        return None
    return knots * 1.15077945


def mi2km(miles):
    """
    Converts to miles to kilometers.
        US Survey Mail = 1609.347219m (Wikipedia)
    """
    if miles is None:
        return None
    return miles * 1.609347219


def mi2nm(miles):
    """
    Converts miles to nautical miles
    """
    if miles is None:
        return None
    return miles * 0.868976


def ft2m(feet):
    """
    Converts feet to meters.
    """
    if feet is None:
        return None
    return feet * 0.3048


def distance(point_a, point_b):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(
        math.radians, [point_a[1], point_a[0], point_b[1], point_b[0]]
    )

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    angle = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    circum = 2 * math.asin(math.sqrt(angle))
    radius = 3956  # Radius of earth in miles. Use 6371 for kilometers
    return circum * radius


def bearing(point_a, point_b):
    """
    Calculates the bearing between two points.

    Found here: https://gist.github.com/jeromer/2005586

    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))

    :Parameters:
      - `point_a: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `point_b: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees

    :Returns:
      The bearing in degrees

    :Returns Type:
      float
    """
    if (type(point_a) != tuple) or (type(point_b) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(point_a[0])
    lat2 = math.radians(point_b[0])

    diff_long = math.radians(point_b[1] - point_a[1])

    x_pos = math.sin(diff_long) * math.cos(lat2)
    y_pos = math.cos(lat1) * math.sin(lat2) - (
        math.sin(lat1) * math.cos(lat2) * math.cos(diff_long)
    )

    initial_bearing = math.atan2(x_pos, y_pos)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing
