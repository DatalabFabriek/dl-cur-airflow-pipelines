CREATE SCHEMA cursus;
CREATE TABLE cursus.weer (
	id SERIAL PRIMARY KEY,
	station integer NOT NULL,
	datum text NOT NULL,
	uur integer NOT NULL,
	windsnelheid DOUBLE PRECISION,
	neerslag DOUBLE PRECISION,
	temperatuur DOUBLE PRECISION
);