from flask import Blueprint, request, Response, json, jsonify
from app.db import get_db
import sqlite3, uuid

lecturer_api = Blueprint('lecturer_api', __name__)

lecturer_fields = ["uuid", "title_before", "first_name", "middle_name", "last_name", "title_after", "picture_url", "location", "claim", "bio", "price_per_hour"]
lecturer_fields_notnull = ["uuid", "first_name", "last_name"]

def NotFound():
    return jsonify({"code": 404, "message": "Daný zdroj nebyl nalezen."}), 404

def DeleteSuccess():
    return jsonify({"code": 204, "message": "Záznam byl úspěšně smazán."}), 204

def MissingFields():
    return jsonify({"code": 400, "message": "Missing mandatory fields."}), 400

def get_tag_uuids_from_lecturer(lecturer_uuid: str) -> list[str]:
    db: sqlite3.Connection = get_db()
    csr: sqlite3.Cursor = db.execute(f"SELECT * FROM lecturer_tags_map WHERE lecturer_uuid = '{lecturer_uuid}'")

    tag_uuids = []

    for row in csr.fetchall():
        tag_uuids.append(row[1])

    return tag_uuids

def get_tag_name(tag_uuid: str) -> str:
    db: sqlite3.Connection = get_db()
    c: sqlite3.Cursor = db.execute(f"SELECT * FROM tags WHERE uuid = '{tag_uuid}'")
    n = c.fetchone()
    if n is None:
        return None
    return n[0]

def get_tag_uuid(name: str) -> str:
    db: sqlite3.Connection = get_db()
    c: sqlite3.Cursor = db.execute(f"SELECT * FROM tags WHERE name = '{name}'")
    u = c.fetchone()
    tuuid = None
    if u is None:
        tuuid = str(uuid.uuid4())
        c = db.execute("INSERT INTO tags (name, uuid) VALUES (?, ?)", [name, tuuid])
        db.commit()
    else:
        tuuid = u[1]
    return tuuid


def get_tags_from_lecturer(lecturer_uuid: str) -> list[object]:
    tag_uuids = get_tag_uuids_from_lecturer(lecturer_uuid)
    tags = []
    for tuuid in tag_uuids:
        tags.append({"name": get_tag_name(tuuid), "uuid": tuuid})
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


def get_lecturer(lecturer_uuid: str):
    db: sqlite3.Connection = get_db()
    c: sqlite3.Cursor = db.execute("SELECT * FROM lecturers WHERE uuid='{}'".format(lecturer_uuid))
    db.commit()

    lecturer_row = c.fetchone()

    if lecturer_row is None:
        return None

    lecturer = {}

    for (i, key) in enumerate(lecturer_row.keys()):
        lecturer[key] = lecturer_row[i]

    lecturer["tags"] = get_tags_from_lecturer(lecturer_uuid)
    lecturer["contact"] = get_contact_from_lecturer(lecturer_uuid)

    return lecturer

@lecturer_api.get("/api/lecturers")
def lecturers_get():
    return get_lecturers() or jsonify([])

@lecturer_api.post("/api/lecturers")
def lecturers_post():
    db: sqlite3.Connection = get_db()
    j = request.json
    lecturer_uuid = str(uuid.uuid4())
    j["uuid"] = lecturer_uuid

    for field in lecturer_fields:
        j[field] = j.get(field)

    for field in lecturer_fields_notnull:
        if j[field] is None:
            return MissingFields()
    db.execute(
        "INSERT INTO lecturers VALUES (:uuid, :title_before, :first_name, :middle_name, "
        ":last_name, :title_after, :picture_url, :location, :claim, :bio, :price_per_hour)", j
    )
    db.commit()

    tags = j.get("tags")
    if not tags is None:
        for (i, tag) in enumerate(tags):
            t = tag
            t["uuid"] = get_tag_uuid(t["name"])
            c = db.execute("INSERT INTO lecturer_tags_map (lecturer_uuid, tag_uuid) VALUES (?, ?)", [lecturer_uuid, t["uuid"]])
            db.commit()
            tags[i] = t
        db.commit()
        j["tags"] = tags

    contact = j.get("contact")
    if contact is None:
        return MissingFields()

    for telnum in contact["telephone_numbers"]:
        c = db.execute("INSERT INTO telnums (telnum, lecturer_uuid) VALUES (?, ?)", [telnum, lecturer_uuid])
        db.commit()

    for email in contact["emails"]:
        c = db.execute("INSERT INTO emails (email, lecturer_uuid) VALUES (?, ?)", [email, lecturer_uuid])
        db.commit()
    return j

@lecturer_api.get("/api/lecturers/<uuid>")
def lecturer_get(uuid: str):
    return get_lecturer(uuid) or NotFound()

@lecturer_api.delete("/api/lecturers/<uuid>")
def lecturer_delete(uuid: str):
    lec = get_lecturer(uuid)
    if lec is None:
        return NotFound()
    
    db: sqlite3.Connection = get_db()
    db.execute("DELETE FROM lecturers WHERE uuid=(?)", [uuid])
    db.commit()
    return DeleteSuccess()


@lecturer_api.put("/api/lecturers/<uuid>")
def lecturer_put(uuid: str):
    lecturer = get_lecturer(uuid)
    if lecturer is None:
        return NotFound()

    lecturer_new = request.json
    updated_keys = []
    for key, val in zip(lecturer_new.keys(), lecturer_new.values()):
        updated_keys.append(key)
        lecturer[key] = val

    db: sqlite3.Connection = get_db()
    cmd = "UPDATE lecturers SET "
    cmd +=  updated_keys[0] + " = '" + str(lecturer[updated_keys[0]]) + "' "
    for key in updated_keys[1::]:
        if key == "tags" or key == "contact" or lecturer.get(key) is None:
            continue
        cmd += ", " + key + " = '" + str(lecturer[key]) + "' "

    cmd += "WHERE uuid='{}'".format(uuid)
    db.execute(cmd)
    db.commit()

    tags = lecturer_new.get("tags")

    if not tags is None:
        db.execute("DELETE FROM lecturer_tags_map WHERE lecturer_uuid='{}'".format(uuid))
        db.commit()

        for (i, tag) in enumerate(tags):
            tuuid = get_tag_uuid(tag["name"])
            tags[i]["uuid"] = tuuid
            
            db.execute("INSERT INTO lecturer_tags_map VALUES (?, ?)", [uuid, tuuid])
            db.commit()

    contact = lecturer_new.get("contact")

    if not contact is None:

        db.execute("DELETE FROM telnums WHERE lecturer_uuid='{}'".format(uuid))
        db.commit()
        db.execute("DELETE FROM emails WHERE lecturer_uuid='{}'".format(uuid))
        db.commit()

        telnums = contact.get("telephone_numbers")
        if not telnums is None:
            for telnum in telnums:
                db.execute("INSERT INTO telnums VALUES (?, ?)", [telnum, uuid])
                db.commit()

        emails = contact.get("emails")
        if not emails is None:
            for email in emails:
                db.execute("INSERT INTO emails VALUES (?, ?)", [email, uuid])
                db.commit()

    return lecturer