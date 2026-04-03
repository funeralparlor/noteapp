from flask import Flask, render_template, request, jsonify
import json, os
from datetime import datetime

app = Flask(__name__)
NOTE_FILE = "soap_note.json"

def load_note():
    if not os.path.exists(NOTE_FILE):
        return {}
    with open(NOTE_FILE, "r") as f:
        return json.load(f)

def save_note(data):
    with open(NOTE_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/note", methods=["GET"])
def get_note():
    return jsonify(load_note())

@app.route("/note", methods=["POST"])
def post_note():
    data = request.get_json()
    save_note(data)
    return jsonify({"status": "ok"})

# Called specifically when user hits Preview — saves with timestamp
@app.route("/note/preview", methods=["POST"])
def preview_note():
    data = request.get_json()
    data["savedAt"] = datetime.now().isoformat()
    save_note(data)
    return jsonify({"status": "ok", "savedAt": data["savedAt"]})

@app.route("/note", methods=["DELETE"])
def delete_note():
    save_note({})
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)