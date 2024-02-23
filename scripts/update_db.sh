#!/bin/bash

wget https://opensky-network.org/datasets/metadata/aircraftDatabase.csv


sqlite3 < load.sql

echo "Should now have a new sqlite3 file that can be moved over the active one "
