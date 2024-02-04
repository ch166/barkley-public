# -*- coding: utf-8 -*-

"""
Geo Calc - Set of geographic calculation functions to work out if a point is inside a box.

Initially targetting two dimensional rectangles, but thinking about the possibility of
using this logic to determine if a plane ; with a lat/lon/altitude and a vertical rate of change
and a direction track is heading into or away from an airport - or just passing overhead.

2D Tests do not consider altitude
3D Tests consider altitude

"""

import datetime
from geopy import distance
from geopy import point


class Geocalc:
    """Class to do simple point inside box / cube tests"""

    def __init__(self, name, lat_s, lat_n, lon_e, lon_w, alt_bottom, alt_top):
        """Init object and set initial values for internals"""
        self.identity = name
        self.latitude_south = lat_s
        self.latitude_north = lat_n
        self.longitude_east = lon_e
        self.longitude_west = lon_w
        self.altitude_lower = alt_bottom
        self.altitude_upper = alt_top
        self.create_time = datetime.datetime.now()
        self.updated_time = datetime.datetime.now()

    def name(self):
        return self.identity

    def inside2D(self, geopoint):
        inside_latitude = False
        inside_longitude = False
        result = False
        if (geopoint.latitude >= self.latitude_south) and (
            geopoint.latitude <= self.latitude_north
        ):
            inside_latitude = True
        if (geopoint.longitude <= self.longitude_east) and (
            geopoint.longitude >= self.longitude_west
        ):
            inside_longitude = True
        if inside_longitude and inside_latitude:
            result = True
        return result

    def inside3D(self, geopoint):
        inside_altitude = False
        result = False

        if (geopoint.altitude >= self.altitude_lower) and (
            geopoint.altitude <= self.altitude_upper
        ):
            inside_altitude = True

        if self.inside2D(point) and inside_altitude:
            result = True
        return result
