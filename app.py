from flask import Flask, render_template, jsonify
 
app = Flask(__name__)
 
@app.route("/health")
def health():
    return jsonify({"status": "ok"})
 
@app.route("/")
def index():
    return render_template("index.html")
 
if __name__ == "__main__":
    app.run(debug=True)
 