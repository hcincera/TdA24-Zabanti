from flask import jsonify, render_template

def APINotFound():
    return jsonify({"code": 404, "message": "Daný zdroj nebyl nalezen."}), 404

def APIDeleteSuccess():
    return jsonify({"code": 204, "message": "Záznam byl úspěšně smazán."}), 204

def APIMissingFields():
    return jsonify({"code": 400, "message": "Missing mandatory fields."}), 400

def NotFound():
    return render_template("errors/404.html"), 404