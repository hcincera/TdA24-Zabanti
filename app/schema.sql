CREATE TABLE IF NOT EXISTS lecturers (
  id TEXT NOT NULL PRIMARY KEY UNIQUE,
  title_before TEXT,
  first_name TEXT NOT NULL,
  middle_name TEXT,
  last_name TEXT NOT NULL,
  title_after TEXT,
  picture_url TEXT,
  location TEXT,
  claim TEXT,
  bio TEXT,
  price_per_hour INTEGER
);

CREATE TABLE IF NOT EXISTS tags (
  name TEXT NOT NULL PRIMARY KEY UNIQUE,
  id TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS telnums (
  num TEXT NOT NULL PRIMARY KEY UNIQUE,
  id INTEGER UNIQUE
);

CREATE TABLE IF NOT EXISTS emails (
  email TEXT NOT NULL UNIQUE,
  id INTEGER UNIQUE
);

CREATE TABLE IF NOT EXISTS lecturer_tags (lecturer_id TEXT NOT NULL, tag_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS lecturer_telnums (lecturer_id TEXT NOT NULL, telnum_id INTEGER);
CREATE TABLE IF NOT EXISTS lecturer_emails (lecturer_id TEXT NOT NULL, email_id INTEGER);