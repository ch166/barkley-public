# barkley
ADS-B bot ; reporting interesting airplane traffic information


Installation is currently manual - requires a couple of no-yet-automated steps.

Install Dir : /opt/barkley
Python VENV : /opt/barkley-venv

Need to make sure that the python environment exists and has the modules from requirements.txt installed

$ python -m venv /opt/barkley-venv


The update_db.sh script needs to be run every so often to get updated ADSB ID data for aircraft.
This script creates the sqlite file - and the resulting file needs to be moved to the data/ directory.


