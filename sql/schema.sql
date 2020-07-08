PRAGMA foreign_keys = ON;

CREATE TABLE route_heights(
  route_id INT UNIQUE,
  height INT,
  PRIMARY KEY(route_id)
);
