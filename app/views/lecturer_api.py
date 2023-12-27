from flask import Blueprint, request, Response, json, jsonify
from app.db import get_db
import sqlite3, uuid

lecturer_api = Blueprint('lecturer_api', __name__)

def get_tag_uuids_from_lecturer(lecturer_uuid: str) -> list[str]:
    db: sqlite3.Connection = get_db()
    csr: sqlite3.Cursor = db.execute(f"SELECT * FROM lecturer_tags_map WHERE lecturer_uuid = '{lecturer_uuid}'")

    tag_uuids = []

    for row in csr.fetchall():
        tag_uuids.append(row[1])

    return tag_uuids

def get_tag_from_id(tag_uuid: str) -> str:
    db: sqlite3.Connection = get_db()
    c: sqlite3.Cursor = db.execute(f"SELECT * FROM tags WHERE uuid = '{tag_uuid}'")
    return c.fetchone()[0]

def get_tags_from_lecturer(lecturer_uuid: str) -> list[object]:
    tag_uuids = get_tag_uuids_from_lecturer(lecturer_uuid)
    tags = []
    for tuuid in tag_uuids:
        tags.append({"name": get_tag_from_id(tuuid), "uuid": tuuid})
    return tags


def get_contact_from_lecturer(lecturer_uuid: str) -> object:
    db: sqlite3.Connection = get_db()

    contact = {}
    telnums = []
    emails = []

    c = db.execute(f"SELECT * FROM telnums WHERE lecturer_uuid = '{lecturer_uuid}'")
    for row in c.fetchall():
        telnums.append(row[0])

    c = db.execute(f"SELECT * FROM emails WHERE lecturer_uuid = '{lecturer_uuid}'")
    for row in c.fetchall():
        emails.append(row[0])

    contact["telephone_numbers"] = telnums
    contact["emails"] = emails

    return contact


def get_lecturers():
    db: sqlite3.Connection = get_db()
    csr: sqlite3.Cursor = db.execute("SELECT * FROM lecturers")

    lecturers = []

    lecturers_rows = csr.fetchall()
    for lecturer_row in lecturers_rows:
        lecturer = {}
        for (i, key) in enumerate(lecturer_row.keys()):
            lecturer[key] = lecturer_row[i]
        lecturer["tags"] = get_tags_from_lecturer(lecturer["uuid"])
        lecturer["contact"] = get_contact_from_lecturer(lecturer["uuid"])
        lecturers.append(lecturer)

    return lecturers



class Lecturer:
    uuid: str
    title_before: str
    first_name: str
    middle_name: str
    last_name: str
    title_after: str
    picture_url: str
    location: str
    claim: str
    bio: str
    tags: [str]
    price_per_hour: int
    contact: {
        "telephone_numbers": [str],
        "emails": [str],
    }

@lecturer_api.get("/api/lecturers")
def lecturers_get():
    return get_lecturers()

@lecturer_api.post("/api/lecturers")
def lecturers_post():
    db: sqlite3.Connection = get_db()
    j = request.json
    lecturer_uuid = str(uuid.uuid4())
    tags = j["tags"]
    contact = j["contact"]

    j["uuid"] = lecturer_uuid
    db.execute(
        "INSERT INTO lecturers VALUES (:uuid, :title_before, :first_name, :middle_name, "
        ":last_name, :title_after, :picture_url, :location, :claim, :bio, :price_per_hour)",
        j
    )
    db.commit()
    for (i, tag) in enumerate(tags):
        t = tag
        n = t["name"]
        c = db.execute(
            "SELECT * FROM tags WHERE name='" + n + "'"
        )
        r = c.fetchone()
        if r is None:
            t["uuid"] = str(uuid.uuid4())
            c = db.execute("INSERT INTO tags (name, uuid) VALUES (:name, :uuid)", t)
            db.commit()
        else:
            t["uuid"] = r["uuid"]

        c = db.execute("INSERT INTO lecturer_tags_map (lecturer_uuid, tag_uuid) VALUES (?, ?)", [lecturer_uuid, t["uuid"]])
        db.commit()
        tags[i] = t
    db.commit()
    j["tags"] = tags

    for telnum in contact["telephone_numbers"]:
        c = db.execute("INSERT INTO telnums (telnum, lecturer_uuid) VALUES (?, ?)", [telnum, lecturer_uuid])
        db.commit()

    for email in contact["emails"]:
        c = db.execute("INSERT INTO emails (email, lecturer_uuid) VALUES (?, ?)", [email, lecturer_uuid])
        db.commit()
    return j