# -*- coding: utf-8 -*-
""" Get data from the Global Aircraft DB """

import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """
    create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as err:
        print(err)

    return None


def find_aircraft_entry(conn, icao_str):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM aircraftDatabase WHERE icao24 = ? ", (icao_str,))

    rows = cur.fetchall()
    if len(rows) > 1:
        return rows[0]
        # print("Global DB - Multiple Rows for " + icao_str)
    return None


def find_aircraft_icao(conn, icao_str):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM aircraftDatabase WHERE icao24 = ? ", (icao_str,))

    rows = cur.fetchall()
    if len(rows) != 1:
        print("Global DB - Duplicate" + icao_str)
    for row in rows:
        print("GlobalDB: " + row[3] + " " + row[4])
