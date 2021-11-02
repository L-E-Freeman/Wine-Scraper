DROP TABLE IF EXISTS wine_list;

CREATE TABLE wine_list (
    wine_name TEXT PRIMARY KEY,
    waitrose_link VARCHAR NOT NULL,
    vivino_link VARCHAR NOT NULL,
    rating INTEGER DEFAULT NULL
);