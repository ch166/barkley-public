"""

Aircraft Class - Manage an Aircraft entity

"""

import datetime


class Aircraft:
    """
    Class to identify objects that are reported to Barkley
    Initially it's all aircraft - but who knows what else turns up
    Initially it's all ADSB data - but as Barkley gets smarter
    we should be able to include more sources
    """

    data = None
    global_db = None
    airport_distance = 0
    create_time = 0
    flutter_sent = 0
    update_counter = 0
    manufacturer = None
    typecode = None
    model = None
    entered_interesting_location = False

    def __init__(self, aircraft_data):
        """Init object and set initial values for internals"""
        self.data = aircraft_data
        self.global_db = []
        self.airport_distance = {}
        self.create_time = datetime.datetime.now()
        self.flutter_sent = 0
        self.update_counter = 0
        self.manufacturer = None
        self.typecode = None
        self.model = None
        self.entered_interesting_location = False

    def created(self):
        """Get created time"""
        return self.create_time

    def fluttered(self):
        """True if this aircraft record is marked as fluttered"""
        result = False
        if self.flutter_sent > 0:
            result = True
        return result

    def hexcode(self):
        """ICAO ADSB Hexcode"""
        result = None
        if "hex" in self.data:
            result = self.data["hex"]
        return result

    def flight(self):
        """Aircraft ICAO Code"""
        result = None
        if "flight" in self.data:
            result = self.data["flight"].strip()
        return result

    def squawk(self):
        """Reported SQUAWK Code"""
        if "squawk" in self.data:
            return self.data["squawk"]
        return None

    def is_emergency(self):
        """
        Emergency Squawk codes
        7700 - Emergency,
        7600 - Comms failure,
        7500 - Hijacking
        """
        result = False
        if "squawk" in self.data:
            squawk_str = self.data["squawk"]
            if squawk_str in ("7700", "7600", "7500"):
                result = True
        return result

    def is_vfr(self):
        """Squawk : 1200"""
        result = False
        if "squawk" in self.data:
            if self.data["squawk"] == "1200":
                result = True
        return result

    def lat(self):
        """Reported latitude"""
        if "lat" in self.data:
            return self.data["lat"]
        return None

    def lon(self):
        """Reported longitude"""
        if "lon" in self.data:
            return self.data["lon"]
        return None

    def gs(self):
        """Reported Ground Speed"""
        if "gs" in self.data:
            return self.data["gs"]
        return None

    def alt(self):
        """Reported Altitude"""
        if "alt_baro" in self.data:
            return self.data["alt_baro"]
        return None

    def category(self):
        """Query Category Record and convert to text version"""
        if "category" in self.data:
            aircraft_category = self.data["category"]
            result = "Raw:" + aircraft_category
            if aircraft_category == "A1":
                result = "Cat:Light"
            if aircraft_category == "A2":
                result = "Cat:Small"
            if aircraft_category in ("A3", "A4"):
                result = "Cat:Large"
            if aircraft_category == "A5":
                result = "Cat:Heavy"
            if aircraft_category == "A7":
                result = "Cat:Rotor"
            return result
        return None

    def get_manufacturer(self):
        """Return the configured manufacturer ID"""
        return self.manufacturer

    def get_model(self):
        """Return the Airplane Model ID"""
        return self.model

    def get_typecode(self):
        """Return ADSB Aircraft Type Code"""
        return self.typecode

    def update_count(self):
        """Return current number of updates against record"""
        return self.update_counter

    def update(self, adsb_record):
        """Process new ADSB record that has the same HEXCODE
        and update fields"""
        result = False
        if adsb_record is None:
            return result
        self.update_counter += 1
        if "flight" not in self.data:
            if "flight" in adsb_record:
                self.data["flight"] = adsb_record["flight"]
                result = True
        if "gs" not in self.data:
            if "gs" in adsb_record:
                self.data["gs"] = adsb_record["gs"]
                result = True
        if "lat" not in self.data:
            if "lat" in adsb_record:
                self.data["lat"] = adsb_record["lat"]
                result = True
        if "lon" not in self.data:
            if "lon" in adsb_record:
                self.data["lon"] = adsb_record["lon"]
                result = True
        if "squawk" not in self.data:
            if "squawk" in adsb_record:
                self.data["squawk"] = adsb_record["squawk"]
                result = True
        if "alt_baro" not in self.data:
            if "alt_baro" in adsb_record:
                self.data["alt_baro"] = adsb_record["alt_baro"]
                result = True

        return result

    def quality_score(self):
        """
        Return True if we have the full set of data including
        hexcode, flight, ground speed, lat, lon, alt and squawk
        """
        quality_score = 0
        if "flight" in self.data:
            quality_score += 1
        if "squawk" in self.data:
            quality_score += 1
        if "gs" in self.data:
            quality_score += 1
        if "lat" in self.data:
            quality_score += 1
        if "lon" in self.data:
            quality_score += 1
        if "alt_baro" in self.data:
            quality_score += 1
        return quality_score

    def update_airport_distance(self, airport, distance):
        """Update distance to airport value"""
        self.airport_distance[airport] = distance

    def get_airport_distance(self, airport):
        """Lookup distance to airport"""
        result = 0
        if airport in self.airport_distance:
            result = self.airport_distance[airport]
        return result

    def quality_record(self):
        """
        Return True if we have the full set of data including
        hexcode, flight, ground speed, lat, lon, alt and squawk
        """
        result = False
        if self.quality_score() == 6:
            result = True
        return result

    def mark_as_fluttered(self):
        """Update the internal flag to mark this
        aircraft as one we've fluttered about"""
        self.flutter_sent = 1

    def update_global_db(self, db_row):
        """Update Aircraft Information based on Global DB Data"""
        if db_row is None:
            return
        self.global_db = db_row
        self.manufacturer = db_row[3]
        if self.manufacturer is not None:
            self.manufacturer = self.manufacturer.split(" ", 1)[0]
        self.model = db_row[4]
        if self.model is not None:
            self.model = self.model.split(" ", 1)[0]
        self.typecode = db_row[5]
        if self.manufacturer is not None:
            self.typecode = self.typecode.split(" ", 1)[0]

    def cardinal(self):
        """Examine ADSB Track information and turn it into a Cardinal Direction"""
        directions = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]
        result = "None"
        if "track" not in self.data:
            return result
        track = self.data["track"]
        index = int((track / 22.5) + 0.5)
        result = directions[(index % 16)]
        return result

    def vsi(self):
        """Retrieve geom_rate : This is the VSI value recorded by dump1090"""
        result = None
        if "geom_rate" in self.data:
            result = self.data["geom_rate"]
        return result

    def set_interesting_location(self):
        """Retrieve geom_rate : This is the VSI value recorded by dump1090"""
        self.entered_interesting_location = True
