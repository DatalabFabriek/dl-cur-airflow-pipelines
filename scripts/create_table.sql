CREATE SCHEMA cur;
CREATE TABLE cur.weer (
	id integer PRIMARY KEY,
	station integer NOT NULL,
	datum text NOT NULL,
	uur integer NOT NULL,
	windsnelheid DOUBLE PRECISION,
	neerslag DOUBLE PRECISION,
	temperatuur DOUBLE PRECISION
)