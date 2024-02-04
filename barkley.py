#!/usr/bin/env python3

"""

 Barkley - Bluesky BOT using ADS-B Source Data

"""

# Standard Library Imports
import os

from dotenv import load_dotenv

# import sys
import time
import random
import datetime
import pickle
import logging
import logging.handlers


# Application Specific Imports
import json

# import atproto

from geopy import distance
from geopy import point

# Pillow Python Image Manipulation
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Barkley Local
import settings
import aircraft
import airports
import debug
import global_aircraft_db
import geocalc

import bluesky

#
# Setup Logging
#
logger = logging.getLogger("barkley")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - \
                              %(name)s - \
                              %(levelname)s - \
                              %(message)s"
)
syslog_handler = logging.handlers.SysLogHandler("/dev/log")
syslog_handler.setLevel(logging.DEBUG)
# logger.setFormatter(formatter)
logger.addHandler(syslog_handler)

# Commenting out for now
# def generate_map_image(aircraft_record, hexcode):
#    fig = plt.figure(figsize=(8, 8))
#
#    # Map (long, lat) to (x, y) for plotting
#   x, y = m(-122.3, 47.6)
#   plt.plot(x, y, 'ok', markersize=5)
#    plt.text(x, y, ' Seattle', fontsize=12);
#    map = Basemap(projection='lcc',
#                  resolution=None,
#                  width=8E6,
#                  height=8E6,
#                  lat_0=45,
#                  lon_0=-100,)
#    map.etopo(scale=0.5, alpha=0.5)
#    plt.show()
#    plt.savefig('test.png')


def random_delay(low, high):
    """Sleep for a random interval between low and high seconds"""
    delay = random.randint(low, high)
    time.sleep(delay)


def generate_temp_image(aircraft_record, hexcode):
    """
    Create a temporary image by laying
        - Aircraft ID
        - Recorded Track
        - Date/Time
        on top of the a base image
    """
    if "hexcode" not in aircraft_record:
        return None
    img = Image.open("sammamish-base-image.png")
    image_file_str = hexcode + "-post_image.png"
    img_font = ImageFont.truetype("Helvetica.ttf", 48)
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), hexcode, (0, 0, 0), font=img_font)
    img.save(image_file_str)
    return image_file_str


def publish_flutter(bluesky_obj, post_str, url_start, url_end, url_string):
    """
    Publish fully formed post to BlueSky.
    Do the necessary error handling and rate limiting
    """
    result = False
    status = None
    # debug.dprint("Attempting to post")
    if settings.get_bool("default", "bluesky_enabled"):
        # debug.dprint("Ready to post")
        try:
            status = bluesky_obj.bluesky_flutter(
                post_str, url_start, url_end, url_string
            )
            debug.dprint("==== post Status ====")
            debug.dprint(status)
            debug.dprint("==== ==== ==== ====")
            result = True
        except Exception as err:
            debug.dprint("bsky Error")
            print(err)
            logger.error(
                "%s - bsky Error: API Code: %s", str(datetime.datetime.now()), err
            )
            result = False
    else:
        logger.debug("Bluesky Disabled")
    random_delay(5, 9)
    return result


def generate_vfr_data(aircraft_set):
    """Generate interesting VFR statistics from current data set"""
    aircraft_flying_vfr_count = 0
    aircraft_count = 0
    for airplane in aircraft_set.get("aircraft"):
        if airplane.get("squawk") == "1200":
            aircraft_flying_vfr_count += 1
        aircraft_count += 1
    logger.info(
        "Aircraft - Count : %d , VFR %d", aircraft_count, aircraft_flying_vfr_count
    )


def handle_new_aircraft(known_aircraft, new_aircraft, global_db):
    """A new aircraft has appeared on the list"""
    new_record = aircraft.Aircraft(new_aircraft)
    known_aircraft[new_record.hexcode()] = new_record
    # global_aircraft_db.find_aircraft_icao(global_db, new_record.hexcode())
    db_row = global_aircraft_db.find_aircraft_entry(global_db, new_record.hexcode())
    known_aircraft[new_record.hexcode()].update_global_db(db_row)
    logger.info(
        "New Aircraft record created - %s , hex: %s",
        new_record.flight(),
        new_record.hexcode(),
    )


def handle_existing_aircraft(known_aircraft, aircraft_record):
    """This is handling any existing aircraft"""
    hexcode = aircraft_record["hex"]
    if known_aircraft[hexcode].update(aircraft_record):
        logger.debug(
            "Aircraft Update - Added useful info (%s:%s)",
            known_aircraft[hexcode].flight(),
            known_aircraft[hexcode].hexcode(),
        )
    logger.debug(
        "Existing Aircraft in area - %s , hex: %s - Upds: (%d)",
        known_aircraft[hexcode].flight(),
        known_aircraft[hexcode].hexcode(),
        known_aircraft[hexcode].update_count(),
    )


def create_flutter(craft, airport_dist):
    """Create the string to post based on Aircraft data"""
    if craft.is_emergency():
        post_str = "**EMER** "
    else:
        post_str = ""
    post_str += "#" + craft.flight()
    if (craft.get_manufacturer() is not None) and (craft.get_model() is not None):
        post_str += " (" + craft.get_manufacturer() + "/" + craft.get_model() + ")"
    if craft.squawk() is not None:
        post_str += " (sqk:" + str(craft.squawk()) + ")"
    post_str += " is in the #PNW,"
    if craft.gs() is not None:
        post_str += " GS:" + str(round(craft.gs())) + "kts,"
    if craft.alt() is not None:
        post_str += " @" + str(craft.alt()) + "ft,"
    if craft.category() is not None:
        post_str += " " + craft.category() + ","
    if airport_dist > 0:
        airport_dist = round(airport_dist)
        post_str += " " + str(airport_dist) + " miles from #SeaTac(#KSEA),"
    craft_direction = craft.cardinal()
    if craft_direction != "None":
        post_str += " Hdg:" + craft_direction + ","
    craft_vsi = craft.vsi()
    if craft_vsi is not None:
        if craft_vsi > 0:
            post_str += " Climb:+" + str(craft_vsi)
        else:
            post_str += " Dscnt:" + str(craft_vsi)
        post_str += "ft/min, "

    url_str = "https://flightaware.com/live/flight/" + craft.flight()
    url_start = len(post_str)
    url_end = url_start + len(url_str)
    post_str += url_str
    # post_str += "https://flightradar24.com/" + craft.flight()
    # post_str += " https://flightradar24.com/" + craft.flight()
    post_str += " #adsb #piaware"
    return (url_start, url_end, post_str, url_str)


def distance_to_airport(airport, lat, lon):
    """Calculate the distance from the airport to the lat/lon values given"""
    if (lat is None) or (lon is None):
        return -1
    # debug.dprint("Creating geo_pos_airport")
    geo_pos_airport = (airport.get_lat(), airport.get_lon())
    # debug.dprint("Creating gep_pos_airplane")
    geo_pos_airplane = (lat, lon)
    # debug.dprint("Calculating Distance")
    geo_distance = distance.distance(geo_pos_airport, geo_pos_airplane).miles
    # debug.dprint("Distance calculations complete")
    return geo_distance


def update_adsb_data(adsb_list, known_aircraft, global_db):
    """
    Iterate over the a set of visible aircraft
    - Check if currently seen aircraft is on recently seen list
    - If aircraft is not currently seen then mark as 'new'
    """
    for aircraft_record in adsb_list:
        # debug.dprint("Entering process_adsb_data loop")
        hexcode = aircraft_record["hex"]
        # Skip aircraft we have already seen about
        if hexcode in known_aircraft:
            # debug.dprint("Found known aircraft " + hexcode)
            handle_existing_aircraft(known_aircraft, aircraft_record)
        else:
            # debug.dprint("Found new aircraft " + hexcode)
            handle_new_aircraft(known_aircraft, aircraft_record, global_db)


def flutter_known_aircraft(known_aircraft, airspace_db, bluesky_obj):
    """Scan list of known aircraft for one that have good data, and not yet posted"""
    for known_list in list(known_aircraft):
        craft = known_aircraft[known_list]
        debug.dprint("Airplane: " + craft.hexcode() + " being examined ")
        # debug.dprint("flutter_known_aircraft")
        # debug.dprint(craft.hexcode())
        if not (craft.quality_record()) or (craft.fluttered()):
            # Skipping records that have
            # - Insufficent data
            # - already been posted
            continue
        debug.dprint(
            "Airplane: " + craft.flight() + " has full data and has not been posted"
        )
        if craft.is_vfr() and settings.get_bool("default", "squawk_1200_hide"):
            logger.info("Skipping VFR flight %s (%s)", craft.flight(), craft.hexcode())
            continue
        aprt_dist = craft.get_airport_distance("ksea")
        if aprt_dist > 150:
            # debug.dprint("Airplane: " +
            #             craft.flight() +
            #             " ( " + str(aprt_dist) + " nm) not at an interesting distance")
            # Skip Distant Planes for now - to slow down the rate of posting
            continue
        debug.dprint("Airplane: " + craft.flight() + " is at an interesting distance")
        if not aircraft_inside_known_area(craft, airspace_db):
            debug.dprint(
                "Airplane: " + craft.flight() + " not in an interesting location"
            )
            continue
        debug.dprint("Airplane: " + craft.flight() + " is in interesting location")

        debug.dprint(
            " post "
            + craft.flight()
            + " ("
            + str(craft.update_count())
            + ") - Dist from ksea "
            + str(aprt_dist)
            + "m"
        )
        (url_start, url_end, post_str, url_string) = create_flutter(craft, aprt_dist)
        # debug.dprint("Aircraft:" + craft.flight() +" Direction :" + craft.cardinal() )
        # logger.info(f"Skipping post of {post_str}")
        flutter_success = publish_flutter(
            bluesky_obj, post_str, url_start, url_end, url_string
        )
        if flutter_success:
            craft.mark_as_fluttered()


def aircraft_inside_known_area(craft, airspace_db):
    """Check to see if the craft is inside any of the known airspaces"""
    craft_location = point.Point(craft.lat(), craft.lon())
    aircraft_inside_area = False
    for airspace_entry in airspace_db:
        airspace = airspace_db[airspace_entry]
        if airspace.inside2D(craft_location):
            aircraft_inside_area = True
    return aircraft_inside_area


def update_aircraft_data(known_aircraft, airport_db, airspace_db):
    """
    Periodically iterate over the a set of known aircraft
    - Update Aircraft 'distance' data to nearest airport (currently KSEA)
    - Check to see if Aircraft are inside interesting airspace
    """

    for craft_entry in known_aircraft:
        craft = known_aircraft[craft_entry]
        for airport_entry in airport_db:
            # debug.dprint(" " + airport_entry)
            airport = airport_db[airport_entry]
            # debug.dprint("airport: " + airport.icaocode() )
            craft_distance = distance_to_airport(airport, craft.lat(), craft.lon())
            # debug.dprint("airport: " + airport.icaocode() + " Distance " + str(distance))
            craft.update_airport_distance(airport_entry, craft_distance)
            # debug.dprint("airport distance updated")
        if aircraft_inside_known_area(craft, airspace_db):
            # Aircraft inside known area
            craft.set_interesting_location()
    return True


def age_out_old_adsb(data_set, interval):
    """Delete entries older than interval seconds ago from the dataset"""
    time_now = datetime.datetime.now()
    deleted_counter = 0
    invisible_counter = 0
    for craftid in list(data_set):
        if data_set[craftid].created() < time_now - datetime.timedelta(
            seconds=interval
        ):
            if data_set[craftid].fluttered() == 0:
                invisible_counter += 1
            # debug.dprint(" Deleting " +
            #             data_set[craftid].hexcode() +
            #             " Score: " +
            #             str(data_set[craftid].quality_score()))
            del data_set[craftid]
            deleted_counter += 1
    debug.dprint(
        "Deleted old records "
        + str(deleted_counter)
        + " - Remaining: "
        + str(len(data_set.keys()))
        + " - Invisible Craft "
        + str(invisible_counter)
    )


def setup_airports(airport_db):
    """Create an initial set of Airport DB entries"""
    new_airport = airports.Airport("kbfi", "bfi", 47.5299722, -122.3019444, 21.6)
    airport_db["kbfi"] = new_airport
    new_airport = airports.Airport("ksea", "sea", 47.4498889, -122.3117778, 423.3)
    airport_db["ksea"] = new_airport
    new_airport = airports.Airport("kpae", "pae", 47.9070000, -122.2815833, 607.5)
    airport_db["kpae"] = new_airport


def setup_airspace(airspace_db):
    """Create an initial set of known Airspace"""
    new_geobox = geocalc.Geocalc(
        "sammamish", 47.557878, 47.673005, -121.976254, -122.586154, 0, 10000
    )
    airspace_db["sammamish"] = new_geobox
    new_geobox = geocalc.Geocalc(
        "seatac", 47.436920, 47.523239, -121.37, -122.30, 0, 10000
    )
    airspace_db["seatac"] = new_geobox


def main():
    """
    Main Entrypoint
    Setup initial requirements
     - Connection to bluesky
     - Connection to FlightAware
    Start Loop
     - Scan list of seen aircraft
     - Identify new target aircraft
     - Generate and publish post
    """

    known_aircraft = dict()
    airport_db = dict()
    airspace_db = dict()

    setup_airports(airport_db)
    setup_airspace(airspace_db)

    global_db = global_aircraft_db.create_connection("data/global_aircraft_db.sqlite3")

    debug.dprint("Loading Settings")
    settings.init()

    load_dotenv()

    BLUESKY_ACCT = os.getenv('BLUESKY_ACCT')
    BLUESKY_AUTH = os.getenv('BLUESKY_AUTH')

    debug.dprint("Logging into bluesky")
    bluesky_obj = bluesky.BlueSky(BLUESKY_ACCT, BLUESKY_AUTH)

    aircraft_max_age = 1800

    debug.dprint("Loading saved dataset")
    if os.path.isfile("data/known_aircraft.pkl"):
        known_aircraft = pickle.load(open("data/known_aircraft.pkl", "rb"))
    else:
        known_aircraft = {}

    counter = 0
    while True:
        try:
            debug.dprint("Starting New Main Loop")
            aircraft_filename = settings.get_string("dump1090", "aircraftjson")
            aircraft_file = open(aircraft_filename)
            adsb_data = json.load(aircraft_file)
            logger.info("data_set Time: %s", time.ctime(adsb_data.get("now")))
            update_adsb_data(adsb_data["aircraft"], known_aircraft, global_db)
            update_aircraft_data(known_aircraft, airport_db, airspace_db)
            #

            flutter_known_aircraft(known_aircraft, airspace_db, bluesky_obj)

            # print(known_aircraft)
            print("------------")

            pickle.dump(known_aircraft, open("data/known_aircraft.pkl", "wb"))
            debug.dprint("Aging out old records")
            age_out_old_adsb(known_aircraft, aircraft_max_age)
            debug.dprint("Ending Main Loop")
        finally:
            aircraft_file.close()
            random_delay(15, 40)
        counter += 1
        # debug.dprint("Completing 1000 loop run")


if __name__ == "__main__":
    main()
