import os

from flask import Flask, jsonify, render_template
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

@app.route('/s')
def sindex():
    return app.send_static_file("index.html");

@app.route('/lecturer')
def frontend_lecturer():
    return app.send_static_file("lecturer.html");

@app.route('/')
def index():
    return render_template("index.html", lecturers=db.get_lecturers())

def get_fullname(lecturer):
    l = db.validate_lecturer_json(lecturer)
    title_before = l["title_before"] + " "
    if title_before == " ":
        title_before = ""
    first_name = l["first_name"] + " "

    middle_name = l["middle_name"] + " "
    if middle_name == " ":
        middle_name = ""
    
    last_name = l["last_name"]

    title_after = " " + l["title_after"]
    if title_after == " ":
        title_after = ""
    
    fullname = title_before + first_name + middle_name + last_name + title_after
    return fullname

app.jinja_env.globals.update(get_fullname=get_fullname)

@app.route('/lecturer/<id>')
def lecturer(id: str):
    print(f"UUID: {id}")
    lecturer = db.get_lecturer(id)
    if lecturer is None:
        return errors.NotFound()
    return render_template("lecturer.html", l=lecturer)

@app.route("/api")
def api():
    secret = {
        "secret": "The cake is a lie",
    }
    return jsonify(secret)


app.register_blueprint(lecturer_api)

if __name__ == '__main__':
    app.run()