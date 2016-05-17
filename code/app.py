#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/', methods=['GET'])
def query_records():
    with open('/tmp/data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        return jsonify(records)


@app.route('/', methods=['PUT'])
def create_record():
    record = json.loads(request.data)
    with open('/tmp/data.txt', 'wr') as f:
        data = f.read()
        if not data:
            records = [record]
        else:
            records = json.loads(data)
            records.append(record)
        f.write(json.dumps(data))
        return jsonify(records)


@app.route('/', methods=['POST'])
def update_record():
    record = json.loads(request.data)
    new_records = []
    with open('/tmp/data.txt', 'wr') as f:
        data = f.read()
        records = json.loads(data)
        for r in records:
            if r['name'] == record['name']:
                r['email'] = record['email']
            new_records.append(r)
        f.write(json.dumps(new_records))
    return jsonify(new_records)


@app.route('/', methods=['DELETE'])
def delte_record():
    record = json.loads(request.data)
    new_records = []
    with open('/tmp/data.txt', 'wr') as f:
        data = f.read()
        records = json.loads(data)
        for r in records:
            if r['name'] == record['name']:
                continue
            new_records.append(r)
        f.write(json.dumps(new_records))
    return jsonify(new_records)

app.run()
