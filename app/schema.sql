CREATE TABLE IF NOT EXISTS lecturers (
  uuid TEXT NOT NULL PRIMARY KEY UNIQUE,
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
  uuid TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS lecturer_tags_map (
  lecturer_uuid TEXT NOT NULL,
  tag_uuid TEXT NOT NULL,
  FOREIGN KEY (lecturer_uuid) REFERENCES lecturers (uuid),
  FOREIGN KEY (tag_uuid) REFERENCES tags (uuid)
);

CREATE TABLE IF NOT EXISTS telnums (
  telnum TEXT NOT NULL UNIQUE,
  lecturer_uuid TEXT NOT NULL,
  FOREIGN KEY (lecturer_uuid) REFERENCES lecturers (uuid)
);

CREATE TABLE IF NOT EXISTS emails (
  email TEXT NOT NULL UNIQUE,
  lecturer_uuid TEXT NOT NULL,
  FOREIGN KEY (lecturer_uuid) REFERENCES lecturers (uuid)
);
