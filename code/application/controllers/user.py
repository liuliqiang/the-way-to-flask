#!/usr/bin/env python
# encoding: utf-8
from flask import Blueprint, jsonify
from flask_jwt import jwt_required, current_identity


user_bp = Blueprint('users', __name__, url_prefix='')


@user_bp.route('/user_info', methods=['POST'])
@jwt_required()
def user_info():
    resp = {"result": 200,
            "data": current_identity.to_json()}
    return jsonify(**resp)
