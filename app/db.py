import click
from flask import current_app, g
from flask.cli import with_appcontext

import sqlite3
import uuid as UUID


def get_con():
    if 'con' not in g:
        g.con = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.con.row_factory = sqlite3.Row

    return g.con


def close_db(e=None):
    con = g.pop('db_con', None)

    if con is not None:
        con.close()


def init_db():
    """
    Inicializuje databázi dle schema.sql
    """
    con = get_con()

    with current_app.open_resource('schema.sql') as f:
        con.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Definujeme příkaz příkazové řádky
    """
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

#
# Lecturer specific stuff
#

@staticmethod
def validate_lecturer_json(json):
    lecturer = json

    uuid = json.get("uuid")
    if uuid is None:
        return None
    title_before = json.get("title_before")

    first_name = json.get("first_name")
    if first_name is None:
        return None

    middle_name = json.get("middle_name")

    last_name = json.get("last_name")
    if last_name is None:
        return None

    title_after = json.get("title_after")
    picture_url = json.get("picture_url")
    location = json.get("location")
    claim = json.get("claim")
    bio = json.get("bio")
    price_per_hour = json.get("price_per_hour")
    if price_per_hour is None:
        return None

    contact = json.get("contact")
    if contact is None:
        return None

    emails = contact.get("emails")
    if emails is None:
        return None
    
    telnums = contact.get("telephone_numbers")
    if telnums is None:
        return None

    tags = json.get("tags", [])
    for (i, tag) in enumerate(tags):
        name = tag.get("name")
        if name is None:
            return None
        tags[i]["uuid"] = tag.get("uuid")

    return {
        "uuid": uuid,
        "title_before": title_before,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "title_after": title_after,
        "picture_url": picture_url,
        "location": location,
        "claim": claim,
        "bio": bio,
        "price_per_hour": price_per_hour,
        "contact": contact,
        "tags": tags
    }

def commit():
    con = get_con()
    con.commit()

def add_lecturer(lecturer):
    con = get_con()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO lecturers VALUES (:uuid, :title_before, :first_name, :middle_name, "
        ":last_name, :title_after, :picture_url, :location, :claim, :bio, :price_per_hour)", lecturer
    )

def add_lecturer_tag(lecturer_uuid, tag):
    con = get_con()
    cur = con.cursor()
    cur.execute("INSERT INTO lecturer_tags_map (lecturer_uuid, tag_uuid) VALUES (?, ?)", [lecturer_uuid, tag["uuid"]])

def add_lecturer_email(lecturer_uuid, email):
    con = get_con()
    cur = con.cursor()
    cur.execute("INSERT INTO emails (email, lecturer_uuid) VALUES (?, ?)", [email, lecturer_uuid])

def add_lecturer_telnum(lecturer_uuid, telnum):
    con = get_con()
    cur = con.cursor()
    cur.execute("INSERT INTO telnums (telnum, lecturer_uuid) VALUES (?, ?)", [telnum, lecturer_uuid])

def get_lecturer_tag_uuids(lecturer_uuid: str) -> list[str]:
    con = get_con()
    cur = con.execute(f"SELECT * FROM lecturer_tags_map WHERE lecturer_uuid = '{lecturer_uuid}'")

    tag_uuids = []

    for row in cur.fetchall():
        tag_uuids.append(row[1])

    return tag_uuids

def get_tag_name(tag_uuid: str) -> str:
    con = get_con()
    cur = con.execute(f"SELECT * FROM tags WHERE uuid = '{tag_uuid}'")
    n = cur.fetchone()
    if n is None:
        return None
    return n[0]

def get_tag_uuid(name: str) -> str:
    con = get_con()
    cur = con.execute(f"SELECT * FROM tags WHERE name = '{name}'")
    u = cur.fetchone()
    tuuid = None
    if u is None:
        tuuid = str(UUID.uuid4())
        cur = con.execute("INSERT INTO tags (name, uuid) VALUES (?, ?)", [name, tuuid])
    else:
        tuuid = u[1]
    return tuuid


def get_lecturer_tags(lecturer_uuid: str) -> list[object]:
    tag_uuids = get_lecturer_tag_uuids(lecturer_uuid)
    tags = []
    for tuuid in tag_uuids:
        tags.append({"name": get_tag_name(tuuid), "uuid": tuuid})
    return tags

def get_lecturer_contact(lecturer_uuid: str) -> object:
    con = get_con()

    contact = {}
    telnums = []
    emails = []

    cur = con.execute(f"SELECT * FROM telnums WHERE lecturer_uuid = '{lecturer_uuid}'")
    for row in cur.fetchall():
        telnums.append(row[0])

    cur = con.execute(f"SELECT * FROM emails WHERE lecturer_uuid = '{lecturer_uuid}'")
    for row in cur.fetchall():
        emails.append(row[0])

    contact["telephone_numbers"] = telnums
    contact["emails"] = emails

    return contact


def get_lecturer(lecturer_uuid: str):
    con = get_con()
    cur = con.execute("SELECT * FROM lecturers WHERE uuid='{}'".format(lecturer_uuid))

    lecturer_row = cur.fetchone()

    if lecturer_row is None:
        return None

    lecturer = {}

    for (i, key) in enumerate(lecturer_row.keys()):
        lecturer[key] = lecturer_row[i]

    lecturer["tags"] = get_lecturer_tags(lecturer_uuid)
    lecturer["contact"] = get_lecturer_contact(lecturer_uuid)

    return lecturer

def get_lecturers():
    con = get_con()
    cur = con.execute("SELECT * FROM lecturers")

    lecturers = []

    lecturers_rows = cur.fetchall()
    for lecturer_row in lecturers_rows:
        lecturer = {}
        for (i, key) in enumerate(lecturer_row.keys()):
            lecturer[key] = lecturer_row[i]
        lecturer["tags"] = get_lecturer_tags(lecturer["uuid"])
        lecturer["contact"] = get_lecturer_contact(lecturer["uuid"])
        lecturers.append(lecturer)

    return lecturers

def delete_lecturer(uuid):
    con = get_con()
    cur = con.cursor()
    lecturer = get_lecturer(uuid)
    if lecturer is None:
        return None
    
    cur.execute("DELETE FROM lecturers WHERE uuid=(?)", [uuid])
    return lecturer

def delete_lecturer_telnums(uuid):
    con = get_con()
    cur = con.cursor()
    cur.execute("DELETE FROM telnums WHERE lecturer_uuid=(?)", [uuid])

def delete_lecturer_emails(uuid):
    con = get_con()
    cur = con.cursor()
    cur.execute("DELETE FROM emails WHERE lecturer_uuid=(?)", [uuid])

def delete_lecturer_tags(uuid):
    con = get_con()
    cur = con.cursor()
    cur.execute("DELETE FROM lecturer_tags_map WHERE lecturer_uuid=(?)", [uuid])

def add_lecturer_telnums(uuid, telnums):
    con = get_con()
    cur = con.cursor()
    data = [(telnum, uuid) for telnum in telnums]
    cur.executemany("INSERT INTO telnums (telnum, lecturer_uuid) VALUES (?, ?)", data)

def add_lecturer_emails(uuid, emails):
    con = get_con()
    cur = con.cursor()
    data = [(email, uuid) for email in emails]
    cur.executemany("INSERT INTO emails (email, lecturer_uuid) VALUES (?, ?)", data)


def get_lecturers_with_tag(uuid, tag):
    con = get_con()
    cur = con.cursor()
    res = cur.execute("SELECT * FROM lecturer_tags_map WHERE uuid=(?)", [tag["uuid"]])
    return [l[0] for l in res.fetchall()]