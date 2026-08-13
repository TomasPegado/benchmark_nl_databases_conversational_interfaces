CREATE TABLE qualifying (
    qualifyId INTEGER PRIMARY KEY AUTOINCREMENT,
    raceId INTEGER DEFAULT 0 NOT NULL,
    driverId INTEGER DEFAULT 0 NOT NULL,
    constructorId INTEGER DEFAULT 0 NOT NULL,
    number INTEGER DEFAULT 0 NOT NULL,
    position INTEGER,
    q1 TEXT,
    q2 TEXT,
    q3 TEXT,
    FOREIGN KEY (constructorId) REFERENCES constructors (constructorId),
    FOREIGN KEY (driverId) REFERENCES drivers (driverId),
    FOREIGN KEY (raceId) REFERENCES races (raceId)
)
CREATE TABLE pitStops (
    raceId INTEGER NOT NULL,
    driverId INTEGER NOT NULL,
    stop INTEGER NOT NULL,
    lap INTEGER NOT NULL,
    time TIME NOT NULL,
    duration TEXT,
    milliseconds INTEGER,
    PRIMARY KEY (raceId, driverId, stop),
    FOREIGN KEY (raceId) REFERENCES races (raceId),
    FOREIGN KEY (driverId) REFERENCES drivers (driverId)
)
CREATE TABLE lapTimes (
    raceId INTEGER NOT NULL,
    driverId INTEGER NOT NULL,
    lap INTEGER NOT NULL,
    position INTEGER,
    time TEXT,
    milliseconds INTEGER,
    PRIMARY KEY (raceId, driverId, lap),
    FOREIGN KEY (driverId) REFERENCES drivers (driverId),
    FOREIGN KEY (raceId) REFERENCES races (raceId)
)
CREATE TABLE driverStandings (
    driverStandingsId INTEGER PRIMARY KEY AUTOINCREMENT,
    raceId INTEGER DEFAULT 0 NOT NULL,
    driverId INTEGER DEFAULT 0 NOT NULL,
    points FLOAT DEFAULT 0 NOT NULL,
    position INTEGER,
    positionText TEXT,
    wins INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY (raceId) REFERENCES races (raceId),
    FOREIGN KEY (driverId) REFERENCES drivers (driverId)
)

CREATE TABLE drivers (
    driverId INTEGER PRIMARY KEY AUTOINCREMENT,
    driverRef TEXT DEFAULT '' NOT NULL,
    number INTEGER,
    code TEXT,
    forename TEXT DEFAULT '' NOT NULL,
    surname TEXT DEFAULT '' NOT NULL,
    dob DATE,
    nationality TEXT,
    url TEXT DEFAULT '' NOT NULL,
    UNIQUE (url)
)

CREATE TABLE constructorStandings (
    constructorStandingsId INTEGER PRIMARY KEY AUTOINCREMENT,
    raceId INTEGER DEFAULT 0 NOT NULL,
    constructorId INTEGER DEFAULT 0 NOT NULL,
    points FLOAT DEFAULT 0 NOT NULL,
    position INTEGER,
    positionText TEXT,
    wins INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY (raceId) REFERENCES races (raceId),
    FOREIGN KEY (constructorId) REFERENCES constructors (constructorId)
)

CREATE TABLE constructors (
    constructorId INTEGER PRIMARY KEY AUTOINCREMENT,
    constructorRef TEXT DEFAULT '' NOT NULL,
    name TEXT DEFAULT '' NOT NULL,
    nationality TEXT,
    url TEXT DEFAULT '' NOT NULL,
    UNIQUE (name)
)

CREATE TABLE constructorResults (
    constructorResultsId INTEGER PRIMARY KEY AUTOINCREMENT,
    raceId INTEGER DEFAULT 0 NOT NULL,
    constructorId INTEGER DEFAULT 0 NOT NULL,
    points REAL,
    status TEXT,
    FOREIGN KEY (raceId) REFERENCES races (raceId),
    FOREIGN KEY (constructorId) REFERENCES constructors (constructorId)
)

CREATE TABLE circuits (
    circuitId INTEGER PRIMARY KEY AUTOINCREMENT,
    circuitRef VARCHAR(255) NOT NULL DEFAULT '',
    name VARCHAR(255) NOT NULL DEFAULT '',
    location VARCHAR(255),
    country VARCHAR(255),
    lat REAL,
    lng REAL,
    alt INTEGER,
    url VARCHAR(255) NOT NULL DEFAULT '',
    UNIQUE (url)
)