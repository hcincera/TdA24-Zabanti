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

@app.route('/')
def index():
    return app.send_static_file("index.html");

@app.route('/lecturer')
def frontend_lecturer():
    return app.send_static_file("lecturer.html");

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
