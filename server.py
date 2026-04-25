from flask import Flask, jsonify, request, send_file, send_from_directory
import json, subprocess, re
from pathlib import Path

app = Flask(__name__)

SOBER_CONFIG = Path.home() / ".var/app/org.vinegarhq.Sober/config/sober/config.json"
ASSETS_DIR   = Path(__file__).parent / "assets"
SOBER_VER    = "1.6.7"


def load_config():
    if not SOBER_CONFIG.exists():
        return {"fflags": {}}
    raw = SOBER_CONFIG.read_text(encoding="utf-8")
    clean = re.sub(r"//.*", "", raw)
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"fflags": {}}


def save_config(cfg: dict):
    SOBER_CONFIG.write_text(json.dumps(cfg, indent=4), encoding="utf-8")


@app.route("/")
def index():
    return send_file("templates/index.html")


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(ASSETS_DIR, filename)


@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_config())


@app.route("/api/config", methods=["POST"])
def post_config():
    save_config(request.json)
    return jsonify({"ok": True})


@app.route("/api/launch", methods=["POST"])
def do_launch():
    subprocess.Popen(["flatpak", "run", "org.vinegarhq.Sober"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return jsonify({"ok": True})


@app.route("/api/info", methods=["GET"])
def info():
    return jsonify({"sober_version": SOBER_VER, "app_version": "1.0.0"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8502, debug=False)
