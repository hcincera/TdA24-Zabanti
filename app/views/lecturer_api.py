from flask import Blueprint, request, Response, json, jsonify
import app.db as db
import app.errors as errors
import sqlite3
import uuid as UUID
import time

lecturer_api = Blueprint('lecturer_api', __name__)

"""
# start timing
start = round(time.time() * 1000)

# end timing
end = round(time.time() * 1000)
duration = end - start
print(f"DEBUG: took {duration} ms")
"""

@lecturer_api.get("/api/lecturers")
def lecturers_get():
    return db.get_lecturers()

@lecturer_api.post("/api/lecturers")
def lecturers_post():
    j = request.json
    lecturer_uuid = str(UUID.uuid4())
    j["uuid"] = lecturer_uuid

    j = db.validate_lecturer_json(j)
    if j is None:
        return errors.APIMissingFields()

    db.add_lecturer(j)


    tags = j["tags"]
    for (i, tag) in enumerate(tags):
        tags[i]["uuid"] = db.get_tag_uuid(tag["name"])
        db.add_lecturer_tag(lecturer_uuid, tag)

    contact = j["contact"]
    for telnum in contact["telephone_numbers"]:
        db.add_lecturer_telnum(lecturer_uuid, telnum)

    for email in contact["emails"]:
        db.add_lecturer_email(lecturer_uuid, email)

    db.commit()
    return j

@lecturer_api.get("/api/lecturers/<uuid>")
def lecturer_get(uuid: str):
    return db.get_lecturer(uuid) or errors.APINotFound()

@lecturer_api.delete("/api/lecturers/<uuid>")
def lecturer_delete(uuid: str):
    if db.delete_lecturer(uuid) is None:
        return errors.APINotFound()

    db.commit()
    return errors.APIDeleteSuccess()


# do not touch this monstrosity
@lecturer_api.put("/api/lecturers/<uuid>")
def lecturer_put(uuid: str):
    con = db.get_con()
    lecturer = db.get_lecturer(uuid)
    if lecturer is None:
        return errors.APINotFound()

    lecturer_new = request.json
    updated_keys = []
    for key, val in zip(lecturer_new.keys(), lecturer_new.values()):
        updated_keys.append(key)
        lecturer[key] = val

    cmd = "UPDATE lecturers SET "
    cmd +=  updated_keys[0] + " = '" + str(lecturer[updated_keys[0]]) + "' "
    for key in updated_keys[1::]:
        if key == "uuid" or key == "tags" or key == "contact" or lecturer.get(key) is None:
            continue
        cmd += ", " + key + " = '" + str(lecturer[key]) + "' "

    cmd += "WHERE uuid='{}'".format(uuid)
    con.execute(cmd)

    tags = lecturer_new.get("tags")

    if not tags is None:
        db.delete_lecturer_tags(uuid)
        for (i, tag) in enumerate(tags):
            tags[i]["uuid"] = db.get_tag_uuid(tag["name"])
            db.add_lecturer_tag(uuid, tags[i])

    contact = lecturer_new.get("contact")

    if not contact is None:

        db.delete_lecturer_telnums(uuid)
        db.delete_lecturer_emails(uuid)

        telnums = contact.get("telephone_numbers")
        if not telnums is None:
            db.add_lecturer_telnums(uuid, telnums)

        emails = contact.get("emails")
        if not emails is None:
            db.add_lecturer_emails(uuid, emails)

        con.commit()
    return lecturer