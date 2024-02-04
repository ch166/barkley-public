#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 08:01:44 2019

@author: Chris Higgins
"""

import datetime


class Airport:
    """Class to identify Airports that are known to Barkley
    Initially it's all location data - but as Barkley gets smarter
    we should be able to include more sources like
    - runway information
    - weather information
    """

    def __init__(self, icao, iata, lat, lon, alt):
        """Init object and set initial values for internals"""
        self.icao = icao
        self.iata = iata
        self.afd_lat = lat
        self.afd_lon = lon
        self.afd_alt = alt
        self.globaldb = []
        self.create_time = datetime.datetime.now()
        self.updated_time = datetime.datetime.now()
        self.update_counter = 0
        self.manufacturer = None
        self.typecode = None
        self.model = None
        self.flutter_sent = None

    def created(self):
        """Get created time"""
        return self.create_time

    def updated(self):
        """Get last updated time"""
        return self.create_time

    def fluttered(self):
        """True if this airport record is marked as fluttered"""
        result = False
        if self.flutter_sent > 0:
            result = True
        return result

    def icaocode(self):
        """airport ICAO (4 letter) code"""
        return self.icao

    def iatacode(self):
        """airport IATA (3 letter) Code"""
        return self.iata

    def get_lat(self):
        """Reported latitude"""
        return self.afd_lat

    def get_lon(self):
        """Reported longitude"""
        return self.afd_lon

    def get_alt(self):
        """Reported Altitude"""
        return self.afd_alt
