"""Flask web application for Gene Keys profile calculator."""

import os
import tempfile
from flask import Flask, render_template, request, send_file, jsonify

from calculator import calculate_profile
from report import generate_report
from genekey_data import GENE_KEYS
from calculator import SEQUENCES

app = Flask(__name__, static_folder=".", static_url_path="")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    date = data.get("date", "").strip()
    time_str = data.get("time", "12:00").strip() or "12:00"
    location = data.get("location", "").strip()

    if not name or not date or not location:
        return jsonify({"error": "Name, date, and location are required."}), 400

    try:
        profile = calculate_profile(date, time_str, location)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    results = {}
    for seq_name, sphere_names in SEQUENCES.items():
        results[seq_name] = []
        for sphere_name in sphere_names:
            info = profile[sphere_name]
            gk = GENE_KEYS[info["gate"]]
            results[seq_name].append({
                "sphere": sphere_name,
                "gate": info["gate"],
                "line": info["line"],
                "shadow": gk["shadow"],
                "gift": gk["gift"],
                "siddhi": gk["siddhi"],
            })

    return jsonify({"results": results, "name": name, "date": date, "time": time_str, "location": location})


@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    name = request.form.get("name", "").strip()
    date = request.form.get("date", "").strip()
    time_str = request.form.get("time", "12:00").strip() or "12:00"
    location = request.form.get("location", "").strip()

    profile = calculate_profile(date, time_str, location)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    generate_report(profile, name, date, time_str, location, tmp.name)

    return send_file(
        tmp.name,
        as_attachment=True,
        download_name=f"{name.replace(' ', '_')}_genekeys.pdf",
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
