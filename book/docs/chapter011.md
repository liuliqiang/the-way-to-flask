# 编写 TODO 应用【part001】

本书前面两个部分分别对 Flask 的基本知识、用法以及介绍了多种扩展以及扩展的通用使用方式，使用扩展过程中的一些细节进行了讲解。虽然过程中有一个 REST API 小例子描述，但是，毕竟是作为各个扩展使用讲解而编排在一块，所以缺乏系统性，全局性。

从本章开始，我将使用 Flask 围绕一个 TODO 应用提供 REST API 进行讲解，让大家有个对 Flask 应用有一个直观的认识。

## TODO 应用讲解

我们需要编写的 TODO 应用主要功能有：

- 可以查询所有待办事项
- 可以查看指定待办事项的详情
- 可以增加一项待办事项
- 可以删除一项待办事项
- 可以修改一项待办事项，包括待办内容，添加标记
- 完成待办事项后可以标记为完成

这些就是我们应用的简略需求，然后再讲一下我们的项目结构，根据前面章节[《更好得维护代码》](chapter007.md)中讲解的，我们将项目结构设计成如下：

	.
	├── README.md
	├── application
	│   ├── __init__.py
	│   ├── controllers
	│   │   ├── __init__.py
	│   │   ├── auth.py
	│   │   ├── todo.py
	│   │   └── user.py
	│   ├── extensions.py
	│   └── models
	│       ├── __init__.py
	│       ├── todo.py
	│       └── user.py
	├── commands.py
	├── config
	│   ├── __init__.py
	│   ├── default.py
	│   ├── development.py
	│   ├── development_sample.py
	│   ├── production.py
	│   ├── production_sample.py
	│   └── testing.py
	├── deploy
	│   ├── flask_env.sh
	│   ├── gunicorn.conf
	│   ├── nginx.conf
	│   └── supervisor.conf
	├── manage.py
	├── pylintrc
	├── requirements.txt
	├── tests
	│   └── __init__.py
	└── wsgi.py

## 设计 Models

Model 的话主要设计两个主要的模型，分别是 User 和 Item。User 表示用户的信息，除了表示TODO 所属人之外，还有登录的用处，而 Item 则是待办事项了，具体设计需要参考需求而定，关于 Model 的具体设计过程不是本章讨论的重点，所以直接给出 Models：

application/models/__init__.py

	#!/usr/bin/env python
	# encoding: utf-8
	from user import *
	from todo import *
	
	
	def all():
	    result = []
	    models = [user, todo]
	
	    for m in models:
	        result += m.__all__
	
	    return result
	
	__all__ = all()

application/models/user.py

	#!/usr/bin/env python
	# encoding: utf-8
	from application.extensions import db
	
	__all__ = ['Role', 'User']
	
	
	class Permission:
	    READ = 0x01
	    CREATE = 0x02
	    UPDATE = 0x04
	    DELETE = 0x08
	    DEFAULT = READ
	
	
	class Role(db.Document):
	    name = db.StringField()
	    permission = db.IntField()
	
	
	class User(db.Document):
	    name = db.StringField()
	    password = db.StringField()
	    email = db.StringField()
	    role = db.ReferenceField('Role')
	
	    def to_json(self):
	        return {"name": self.name,
	                "email": self.email,
	                "role": self.role.name}
	
	    def is_authenticated(self):
	        return True
	
	    def is_active(self):
	        return True
	
	    def is_anonymous(self):
	        return False
	
	    def get_id(self):
	        return str(self.id)

application/models/todo.py

	#!/usr/bin/env python
	# encoding: utf-8
	from application.extensions import db
	
	__all__ = ['Item']
	
	
	class Item(db.Document):
	    content = db.StringField(required=True)
	    created_date = db.DateTimeField()
	    completed = db.BooleanField(default=False)
	    completed_date = db.DateTimeField()
	    created_by = db.ReferenceField('User', required=True)
	    notes = db.ListField(db.StringField())
	    priority = db.IntField()
	
	    def __repr__(self):
	        return "<Item: {} Content: {}>".format(str(self.id),
	                                               self.content)
	
	    def to_json(self):
	        return {
	            'id': str(self.id),
	            'content': self.content,
	            'completed': self.completed,
	            'completed_at': self.completed_date.strftime("%Y-%m-%d %H:%M:%S") if self.completed else "",
	            'created_by': self.created_by.name,
	            'notes': self.notes,
	            'priority': self.priority
	        }

## 设计 views

根据我们在前面章节所学习的知识，我们这个应用的 views 就不是直接使用 `app.route` 来绑定 URL 了，而是使用 Blueprint 来设计，具体设计如下：

application/controller/__init__.py

	#!/usr/bin/env python
	# encoding: utf-8
	import auth
	import user
	import todo
	
	all_bp = [
	    auth.auth_bp,
	    user.user_bp,
	    todo.todo_bp
	]

application/controller/auth.py

	#!/usr/bin/env python
	# encoding: utf-8
	import json
	
	from flask import Blueprint, request, jsonify
	from flask.ext.login import login_user, logout_user
	
	import application.models as Models
	
	
	auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
	
	
	@auth_bp.route('/login', methods=['POST'])
	def login():
	    info = json.loads(request.data)
	    username = info.get('username', 'guest')
	    password = info.get('password', '')
	
	    user = Models.User.objects(name=username,
	                               password=password).first()
	    if user:
	        login_user(user)
	        return jsonify(user.to_json())
	    else:
	        return jsonify({"status": 401,
	                        "reason": "Username or Password Error"})
	
	
	@auth_bp.route('/logout', methods=['POST'])
	def logout():
	    logout_user()
	    return jsonify(**{'result': 200,
	                      'data': {'message': 'logout success'}})

application/controller/user.py

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

application/controller/todo.py

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

## 初始化扩展

扩展我们是统一放到 application/extensions.py 里面进行构建对象的，所以文件有：

application/extensions.py

	#!/usr/bin/env python
	# encoding: utf-8
	from flask.ext.admin import Admin
	from flask.ext.login import LoginManager
	from flask.ext.mongoengine import MongoEngine
	
	
	db = MongoEngine()
	login_manager = LoginManager()
	admin = Admin()

## 初始化应用

	#!/usr/bin/env python
	# encoding: utf-8
	import sys
	import logging
	
	from flask import Flask
	from flask_admin.contrib.mongoengine import ModelView
	
	from config import load_config
	from application.extensions import db, login_manager, admin
	from application.models import User, Role
	from application.controllers import all_bp
	
	# convert python's encoding to utf8
	try:
	    reload(sys)
	    sys.setdefaultencoding('utf8')
	except (AttributeError, NameError):
	    pass
	
	
	def create_app(mode):
	    """Create Flask app."""
	    config = load_config(mode)
	
	    app = Flask(__name__)
	    app.config.from_object(config)
	
	    if not hasattr(app, 'production'):
	        app.production = not app.debug and not app.testing
	
	    if app.debug or app.testing:
	        # Log errors to stderr in production mode
	        app.logger.addHandler(logging.StreamHandler())
	        app.logger.setLevel(logging.ERROR)
	
	    # Register components
	    register_extensions(app)
	    register_blueprint(app)
	
	    return app
	
	
	def register_extensions(app):
	    """Register models."""
	    db.init_app(app)
	    login_manager.init_app(app)
	
	    # flask-admin configs
	    admin.init_app(app)
	    admin.add_view(ModelView(User))
	    admin.add_view(ModelView(Role))
	
	    login_manager.login_view = 'auth.login'
	
	    @login_manager.user_loader
	    def load_user(user_id):
	        return User.objects(id=user_id).first()
	
	
	def register_blueprint(app):
	    for bp in all_bp:
	        app.register_blueprint(bp)


