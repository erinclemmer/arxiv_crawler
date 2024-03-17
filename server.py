import os
import json

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.debug = False
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/api/project/list', methods=['GET'])
@cross_origin()
def process_async():
    projects = []
    for project in os.listdir('projects'):
        with open('projects/' + project, 'r') as f:
            projects.append(json.load(f))
    
    return jsonify(projects), 200

@app.route('/api/project/create', methods=["POST", "OPTIONS"])
@cross_origin()
def create_project():
    data = request.json
    if not 'name' in data:
        return jsonify({ "Error": "No name provided "}), 200
    name = data["name"]
    num_projects = len(os.listdir('projects'))
    with open(f'projects/{name}.json', 'w') as f:
        json.dump({
            "id": num_projects + 1,
            "name": name
        }, f)
    return jsonify({ "Error": None }), 200

if __name__ == '__main__':
    app.run(port=4000)