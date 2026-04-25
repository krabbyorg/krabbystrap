from flask import Flask, jsonify, request, send_file, send_from_directory
import json, subprocess, re, urllib.request, urllib.error, zipfile, shutil, os, threading
from pathlib import Path

app = Flask(__name__)

SOBER_CONFIG    = Path.home() / ".var/app/org.vinegarhq.Sober/config/sober/config.json"
SOBER_OVERLAY   = Path.home() / ".var/app/org.vinegarhq.Sober/data/sober/asset_overlay"
SOBER_ASSETS    = Path.home() / ".var/app/org.vinegarhq.Sober/data/sober/assets"
ASSETS_DIR      = Path(__file__).parent / "assets"
KRABBY_DIR      = Path.home() / "Documents/Krabbystrap"
MARKETPLACE_DIR = KRABBY_DIR / "Marketplace"
INSTALLED_DB    = KRABBY_DIR / "installed.json"
SOBER_VER       = "1.6.7"

GH_RAW = "https://raw.githubusercontent.com/Wookhq/Lution-Marketplace/main/"
MARKETPLACE_URLS = {
    "mods_content":   GH_RAW + "Assets/Mods/content.json",
    "mods_info":      GH_RAW + "Assets/Mods/info.json",
    "themes_content": GH_RAW + "Assets/Themes/content.json",
    "themes_info":    GH_RAW + "Assets/Themes/info.json",
    "fflags_content": GH_RAW + "Assets/FastFlag/index.json",
}

# ── helpers ────────────────────────────────────────────────────────────────

def _fetch(url: str, timeout=10) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Krabbystrap/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def _fetch_json(url: str) -> list | dict:
    return json.loads(_fetch(url))

# ── sober config ───────────────────────────────────────────────────────────

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

# ── installed tracking ─────────────────────────────────────────────────────

def _load_installed() -> dict:
    KRABBY_DIR.mkdir(parents=True, exist_ok=True)
    if not INSTALLED_DB.exists():
        return {"mods": [], "themes": []}
    try:
        return json.loads(INSTALLED_DB.read_text())
    except Exception:
        return {"mods": [], "themes": []}

def _save_installed(db: dict):
    INSTALLED_DB.write_text(json.dumps(db, indent=2))

# ── in-memory cache (reset on /refresh) ───────────────────────────────────
_cache: dict = {}
_cache_lock = threading.Lock()

def _get_cached(key: str, url: str, refresh=False):
    with _cache_lock:
        if key not in _cache or refresh:
            _cache[key] = _fetch_json(url)
        return _cache[key]

# ── Flask routes ───────────────────────────────────────────────────────────

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

# ── Marketplace ────────────────────────────────────────────────────────────

@app.route("/api/marketplace/all", methods=["GET"])
def marketplace_all():
    refresh = request.args.get("refresh") == "1"
    try:
        mods    = _get_cached("mods_content",   MARKETPLACE_URLS["mods_content"],   refresh)
        themes  = _get_cached("themes_content",  MARKETPLACE_URLS["themes_content"],  refresh)
        fflags  = _get_cached("fflags_content",  MARKETPLACE_URLS["fflags_content"],  refresh)
        m_info  = _get_cached("mods_info",       MARKETPLACE_URLS["mods_info"],       refresh)
        t_info  = _get_cached("themes_info",     MARKETPLACE_URLS["themes_info"],     refresh)
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    installed = _load_installed()
    inst_mods   = set(installed.get("mods", []))
    inst_themes = set(installed.get("themes", []))

    # attach download path + installed flag to each mod/theme card
    m_map = {i["name"]: i["path"] for i in m_info}
    t_map = {i["name"]: i["path"] for i in t_info}

    for m in mods:
        m["_dl"] = m_map.get(m.get("title", ""))
        m["_installed"] = m.get("title", "") in inst_mods

    for t in themes:
        t["_dl"] = t_map.get(t.get("title", ""))
        t["_installed"] = t.get("title", "") in inst_themes

    return jsonify({"mods": mods, "themes": themes, "fflags": fflags})


@app.route("/api/marketplace/install", methods=["POST"])
def marketplace_install():
    data  = request.json or {}
    name  = data.get("name", "").strip()
    kind  = data.get("type", "")   # "mod" or "theme"
    if not name or kind not in ("mod", "theme"):
        return jsonify({"error": "bad params"}), 400

    info_key = "mods_info" if kind == "mod" else "themes_info"
    info_url = MARKETPLACE_URLS["mods_info" if kind == "mod" else "themes_info"]

    try:
        info_list = _get_cached(info_key, info_url)
        entry = next((i for i in info_list if i["name"] == name), None)
        if not entry:
            return jsonify({"error": f"'{name}' not found in info.json"}), 404

        dl_url = GH_RAW + entry["path"]
        dest_dir = MARKETPLACE_DIR / (kind + "s") / name
        dest_dir.mkdir(parents=True, exist_ok=True)

        zip_bytes = _fetch(dl_url, timeout=30)
        zip_path  = dest_dir / (name + ".zip")
        zip_path.write_bytes(zip_bytes)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dest_dir)
        zip_path.unlink()

        db = _load_installed()
        lst = db.setdefault(kind + "s", [])
        if name not in lst:
            lst.append(name)
        _save_installed(db)

        return jsonify({"ok": True, "path": str(dest_dir)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _copy_tree(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        s, d = item, dst / item.name
        if s.is_dir():
            if d.exists():
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)


@app.route("/api/marketplace/apply", methods=["POST"])
def marketplace_apply():
    data = request.json or {}
    name = data.get("name", "").strip()
    kind = data.get("type", "")
    if not name or kind not in ("mod", "theme"):
        return jsonify({"error": "bad params"}), 400

    src = MARKETPLACE_DIR / (kind + "s") / name
    if not src.exists():
        return jsonify({"error": "not installed"}), 404

    try:
        SOBER_OVERLAY.mkdir(parents=True, exist_ok=True)
        for folder in ("ExtraContent", "content", "ClientSettings", "PlatformContent"):
            s = src / folder
            if s.exists():
                _copy_tree(s, SOBER_OVERLAY / folder)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/marketplace/remove", methods=["POST"])
def marketplace_remove():
    data = request.json or {}
    name = data.get("name", "").strip()
    kind = data.get("type", "")
    if not name or kind not in ("mod", "theme"):
        return jsonify({"error": "bad params"}), 400

    path = MARKETPLACE_DIR / (kind + "s") / name
    if path.exists():
        shutil.rmtree(path)

    db  = _load_installed()
    lst = db.get(kind + "s", [])
    if name in lst:
        lst.remove(name)
    _save_installed(db)
    return jsonify({"ok": True})


@app.route("/api/marketplace/reset", methods=["POST"])
def marketplace_reset():
    try:
        if not SOBER_ASSETS.exists():
            return jsonify({"error": "Sober assets dir not found — launch Roblox once first"}), 404
        if SOBER_OVERLAY.exists():
            shutil.rmtree(SOBER_OVERLAY)
        SOBER_OVERLAY.mkdir(parents=True)
        _copy_tree(SOBER_ASSETS, SOBER_OVERLAY)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/marketplace/fflag-apply", methods=["POST"])
def fflag_apply():
    data     = request.json or {}
    inst_url = data.get("install", "")
    if not inst_url:
        return jsonify({"error": "missing install path"}), 400
    try:
        raw  = _fetch(GH_RAW + inst_url)
        blob = json.loads(raw)
        flags = blob.get("fastflag") or blob.get("fflags") or blob
        if not isinstance(flags, dict):
            return jsonify({"error": "unexpected fflag format"}), 502
        cfg = load_config()
        cfg.setdefault("fflags", {}).update(flags)
        save_config(cfg)
        return jsonify({"ok": True, "applied": len(flags)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/marketplace/installed", methods=["GET"])
def marketplace_installed():
    return jsonify(_load_installed())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8502, debug=False)
