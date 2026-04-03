from flask import Flask, render_template, request, jsonify
import json, os, re
from datetime import datetime

app = Flask(__name__)
NOTES_DIR = "notes"

# Make sure notes directory exists
os.makedirs(NOTES_DIR, exist_ok=True)


def safe_filename(name):
    """Turn a customer name into a safe filename."""
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9_\- ]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name or "unnamed"


def note_path(filename):
    return os.path.join(NOTES_DIR, filename + ".json")


def load_note_by_file(filename):
    path = note_path(filename)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def save_note_to_file(filename, data):
    path = note_path(filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def list_all_notes():
    """Return all note filenames sorted by last modified (newest first)."""
    files = []
    for f in os.listdir(NOTES_DIR):
        if f.endswith(".json"):
            full = os.path.join(NOTES_DIR, f)
            files.append((f[:-5], os.path.getmtime(full)))
    files.sort(key=lambda x: x[1], reverse=True)
    return [f[0] for f in files]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/notes/list", methods=["GET"])
def get_notes_list():
    return jsonify(list_all_notes())


@app.route("/note/find", methods=["GET"])
def find_note():
    """Find a note by customer name — returns it if exists, or signals to create."""
    customer = request.args.get("customer", "").strip()
    if not customer:
        return jsonify({"found": False})
    filename = safe_filename(customer)
    data = load_note_by_file(filename)
    if data:
        return jsonify({"found": True, "filename": filename, "data": data})
    return jsonify({"found": False, "filename": filename})


@app.route("/note/load/<filename>", methods=["GET"])
def load_note(filename):
    data = load_note_by_file(filename)
    if data is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(data)


@app.route("/note/save", methods=["POST"])
def save_note():
    body = request.get_json()
    customer = body.get("customer", "").strip()
    filename = safe_filename(customer) if customer else "unnamed"
    body["filename"] = filename
    body["savedAt"] = datetime.now().isoformat()
    save_note_to_file(filename, body)
    return jsonify({"status": "ok", "filename": filename, "savedAt": body["savedAt"]})


@app.route("/note/preview", methods=["POST"])
def preview_note():
    body = request.get_json()
    customer = body.get("customer", "").strip()
    filename = safe_filename(customer) if customer else "unnamed"
    body["filename"] = filename
    body["savedAt"] = datetime.now().isoformat()
    body["previewedAt"] = body["savedAt"]
    save_note_to_file(filename, body)
    return jsonify({"status": "ok", "filename": filename, "savedAt": body["savedAt"]})


@app.route("/note/delete/<filename>", methods=["DELETE"])
def delete_note(filename):
    path = note_path(filename)
    if os.path.exists(path):
        os.remove(path)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)