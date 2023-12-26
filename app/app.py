import os

from flask import Flask, jsonify, render_template
from . import db

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
def frontend():
    return app.send_static_file("index.html");

@app.route("/api")
def api():
    secret = {
        "secret": "The cake is a lie",
    }
    return jsonify(secret)


app.register_blueprint(lecturer_api)

if __name__ == '__main__':
    app.run()
