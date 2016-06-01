#!/usr/bin/env python
# encoding: utf-8
import json
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask.ext.login import current_user, login_required

import application.models as Models


todo_bp = Blueprint('todos', __name__, url_prefix='/todo')


@todo_bp.route('/item', methods=['POST'])
@login_required
def create_todo_item():
    data = json.loads(request.data)
    content = data.get('content')
    note = data.get('note', None)
    priority = data.get('priority', 0)

    if not content:
        return jsonify({
            'data': {},
            'msg': 'no content',
            'code': 1001,
            'extra': {}})

    item = Models.Item(content=content, created_date=datetime.now(),
                       completed=False, created_by=current_user.id,
                       notes=[note] if note else [],
                       priority=priority)
    item.save()
    return jsonify({
        'data': item.to_json(),
        'msg': 'create item success',
        'code': 1000,
        'extra': {}
    })


@todo_bp.route('/item', methods=['DELETE'])
@login_required
def delete_todo_item():
    data = json.loads(request.data)
    id = data.get('id')

    if not id:
        return jsonify({
            'data': {},
            'msg': 'no id',
            'code': 2001,
            'extra': {}})

    item = Models.Item.objects(id=id).first()
    item.delete()
    return jsonify({
        'data': item.to_json(),
        'msg': 'delete item success',
        'code': 2000,
        'extra': {}
    })


@todo_bp.route('/item', methods=['PUT'])
@login_required
def update_todo_item():
    data = json.loads(request.data)
    id = data.get('id')
    type = data.get('type')

    if type == "update_content":
        content = data.get('content')
        Models.Item.objects(id=id).first().update(content=content)
    elif type == "insert_notes":
        note = data.get('note')
        Models.Item.objects(id=id).first().update(push__notes=note)
    elif type == "done":
        Models.Item.objects(id=id).first().update(completed=True,
                                                  completed_date=datetime.now())
    return jsonify({
        'data': {'oper': type,
                 'id': id},
        'msg': 'oper done',
        'code': 3000,
        'extra': {}
    })


@todo_bp.route('/item', methods=['GET'])
@login_required
def get_todo_item():
    query_string = request.args.get('q')
    data = json.loads(query_string)
    id = data.get('id')

    item = Models.Item.objects(id=id).first()
    return jsonify({
        'data': item.to_json(),
        'msg': 'query item success',
        'code': 4000,
        'extra': {}
    })


@todo_bp.route('/items', methods=['GET'])
@login_required
def get_todo_items():
    data = json.loads(request.args.get('q'))
    page = data.get('page', 1)
    page_size = data.get('page_size', 10)

    begin = (page - 1) * page_size
    end = begin + page_size
    items = Models.Item.objects()[begin: end]
    rsts = []
    for item in items:
        rsts.append(item.to_json())

    return jsonify({
        'data': rsts,
        'msg': 'query items success',
        'code': 5000,
        'extra': {}
    })
