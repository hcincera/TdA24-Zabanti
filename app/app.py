import os

from flask import Flask, jsonify, render_template, send_from_directory
from . import db
from . import errors

from app.views.lecturer_api import lecturer_api

app = Flask(__name__)

app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db.init_app(app)

@app.route('/')
def index():
    return render_template("catalogue.html", lecturers=db.get_lecturers(), title="TdA Žabanti")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static"),"favicon.ico", mimetype="image/vnd.microsoft.icon")

def get_fullname(lecturer):
    l = db.validate_lecturer_json(lecturer)
    title_before = (l["title_before"] or "") + " "
    if title_before == " ":
        title_before = ""
    first_name = l["first_name"] + " "

    middle_name = (l["middle_name"] or "") + " "
    if middle_name == " ":
        middle_name = ""
    
    last_name = l["last_name"]

    title_after = ", " + (l["title_after"] or "")
    if title_after == ", ":
        title_after = ""
    
    fullname = title_before + first_name + middle_name + last_name + title_after
    return fullname

app.jinja_env.globals.update(get_fullname=get_fullname)

def get_redirect_code(lecturer):
    return "window.location = '../lecturer/" + lecturer["uuid"] + "'"

app.jinja_env.globals.update(get_redirect_code=get_redirect_code)

def get_tags(lecturer):
    s = ""
    for (i, tag) in enumerate(lecturer["tags"]):
        s += tag["name"]
        if i + 1 < len(lecturer["tags"]):
            s += ", "
    return s

app.jinja_env.globals.update(get_tags=get_tags)

def get_emails(lecturer):
    s = ""
    for (i, email) in enumerate(lecturer["contact"]["emails"]):
        s += email
        if i + 1 < len(lecturer["contact"]["emails"]):
            s += ", "
    return s

app.jinja_env.globals.update(get_emails=get_emails)

def get_telnums(lecturer):
    s = ""
    for (i, telnum) in enumerate(lecturer["contact"]["telephone_numbers"]):
        s += telnum
        if i + 1 < len(lecturer["contact"]["telephone_numbers"]):
            s += ", "
    return s

app.jinja_env.globals.update(get_telnums=get_telnums)

@app.route('/lecturer/<id>')
def lecturer(id: str):
    print(f"UUID: {id}")
    lecturer = db.get_lecturer(id)
    if lecturer is None:
        return errors.NotFound()
    return render_template("lecturer.html", lecturer=lecturer)

@app.route("/api")
def api():
    secret = {
        "secret": "The cake is a lie",
    }
    return jsonify(secret)

@app.route('/profile')
def profile():
    return render_template("profile.html", title="Your Profile")

app.register_blueprint(lecturer_api)

if __name__ == '__main__':
    app.run()
