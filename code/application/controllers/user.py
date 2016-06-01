#!/usr/bin/env python
# encoding: utf-8
from flask.ext.login import current_user
from flask import Blueprint, jsonify


user_bp = Blueprint('users', __name__, url_prefix='')


@user_bp.route('/user_info', methods=['POST'])
def user_info():
    if current_user.is_authenticated:
        resp = {"result": 200,
                "data": current_user.to_json()}
    else:
        resp = {"result": 401,
                "data": {"message": "user no login"}}
    return jsonify(**resp)
