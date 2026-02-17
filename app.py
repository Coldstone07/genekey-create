"""Flask API server for Gene Keys profile calculator."""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from calculator import calculate_profile_from_coords, SEQUENCES
from genekey_data import GENE_KEYS

app = Flask(__name__)
CORS(app, origins=[
    "https://coldstone07.github.io",
    "http://localhost:*",
    "http://127.0.0.1:*"
])


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json(silent=True) or {}
    name     = data.get("name", "").strip()
    date     = data.get("date", "").strip()
    time_str = data.get("time", "12:00").strip() or "12:00"
    lat      = data.get("lat")
    lon      = data.get("lon")

    if not name or not date or lat is None or lon is None:
        return jsonify({"error": "Name, date, and coordinates are required."}), 400

    try:
        profile = calculate_profile_from_coords(date, time_str, float(lat), float(lon))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    results = {}
    for seq_name, sphere_names in SEQUENCES.items():
        results[seq_name] = []
        for sn in sphere_names:
            info = profile[sn]
            gk = GENE_KEYS[info["gate"]]
            results[seq_name].append({
                "sphere": sn,
                "gate": info["gate"],
                "line": info["line"],
                "shadow": gk["shadow"],
                "gift": gk["gift"],
                "siddhi": gk["siddhi"],
            })

    return jsonify({"results": results, "name": name, "date": date, "time": time_str})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
