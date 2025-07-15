from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/data')
def data():
    with open("data/africa_policy_data.json") as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/geo')
def geo():
    with open("data/africa.geojson") as f:
        geo = json.load(f)
    return jsonify(geo)

if __name__ == '__main__':
    app.run(debug=True)
