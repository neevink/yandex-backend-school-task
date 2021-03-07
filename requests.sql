CREATE TABLE IF NOT EXISTS TABLE Couriers(
    courier_id INTEGER PRIMARY KEY,
    courier_type INTEGER NOT NULL,
    regions_id INTEGER NOT NULL,
    working_hours TEXT NOT NULL,
);


