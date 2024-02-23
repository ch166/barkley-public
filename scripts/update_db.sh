#!/bin/bash

wget https://opensky-network.org/datasets/metadata/aircraftDatabase.csv

# FIXME: Need to find and eliminate duplicate records or the sqlite process
# will fail to create an index

sqlite3 < load.sql

echo "Should now have a new sqlite3 file that can be moved over the active one "
