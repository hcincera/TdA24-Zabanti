from flask import Blueprint, request, Response, json, jsonify
from app.db import get_db
import sqlite3, uuid

lecturer_api = Blueprint('lecturer_api', __name__)

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
def get_lecturers():
    db: sqlite3.Connection = get_db()
    csr: sqlite3.Cursor = db.execute("SELECT * FROM lecturers")
    return jsonify(csr.fetchall())

@lecturer_api.post("/api/lecturers")
def post_lecturers():
    db: sqlite3.Connection = get_db()
    j = request.json
    id = str(uuid.uuid4())
    tags = j["tags"]
    contact = j["contact"]
    db.execute(
        "INSERT INTO lecturers"
        " (id, title_before, first_name, middle_name, last_name, "
        "title_after, picture_url, location, claim, bio, price_per_hour) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (id, j["title_before"], j["first_name"], j["middle_name"],
        j["last_name"], j["title_after"], j["picture_url"], j["location"],
        j["claim"], j["bio"], j["price_per_hour"])
    )
    db.commit()
    for (i, tag) in enumerate(tags):
        t = tag
        c = db.execute(
            "SELECT * FROM tags WHERE name=:name;", t
        )
        db.commit()
        r = c.fetchone()
        if r is None:
            t["uuid"] = str(uuid.uuid4())
            c = db.execute("INSERT INTO tags (name, id) VALUES (?, ?)", [t["name"], t["uuid"]])
            db.commit()
        else:
            t["uuid"] = r["id"]
        tags[i] = t
    j["uuid"] = id
    j["tags"] = tags
    return j

@lecturer_api.route("/api/lecturers")
def lectuer_api():
    return "list of accounts"