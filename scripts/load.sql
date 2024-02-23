
.mode csv
.import aircraftDatabase.csv aircraftDatabase

CREATE UNIQUE INDEX `icao hex code` on `aircraftDatabase` ( `icao24` ASC ) ;

.save global_db.sqlite3
.quit


