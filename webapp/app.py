"""
EV Charging Demand Forecast — simple web UI

Serves a dropdown-driven dashboard over precomputed model results.
Run with: python app.py, then open http://127.0.0.1:5000
"""

import json
import os

from flask import Flask, jsonify, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_json(filename):
    with open(os.path.join(BASE_DIR, filename)) as f:
        return json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/results")
def api_results():
    """Returns model metrics table + full chart series (actual + all model predictions)."""
    chart_data = load_json("chart_data_full.json")
    results_meta = load_json("results_meta.json")
    return jsonify({"chart": chart_data, "metrics": results_meta})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
