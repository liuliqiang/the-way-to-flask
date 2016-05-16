#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({'name': 'tyrael',
                    'email': 'liqianglau@outlook.com'})

app.run()
