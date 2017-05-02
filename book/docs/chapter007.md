# 规范结构维护代码

到本章为止，我们的 DEMO 程序功能已经日益强大，增删改查，用户登录，权限控制，数据库操作，功能已经有点复杂了，然后看看代码，发现也已经差不多 200 行了。这时，我们不禁要想，难道我们要在这一个 `app.py` 文件中继续编写下去吗？感觉每次添加新的功能好像都是在头(添加引用)在尾(添加逻辑)添加代码，难道这是正确的做法吗？

很显然，作为有洁癖的工程师，肯定不能容忍所有代码都这么一团塞在一个文件里面的，所以我们至少会想到拆分代码然后放到几个模块里面，例如什么 model.py, controller.py 啊之类的。但是，作为有深度洁癖的人，觉得把一大堆文件放在一个目录里面也是件糟心的事，所以，这里我要介绍一下我比较推荐的代码目录结构。

## Flask 代码目录结构

虽然目录结构见仁见智，个人有个人的看法和习惯，但总的来说，经过很多人的实践和总结，还是有很多共同的意见和想法的，而我在查看他人的目录结构结合自身在工作中的使用经验，总结了一个个人认为比较恰当的目录结构供参考，而本书也是以这个目录结构为架构进行下去的。

我推荐的目录结构：

	.
	├── README.md
	├── application
	│   ├── __init__.py
	│   ├── controllers
	│   │   └── __init__.py
	│   ├── forms
	│   │   └── __init__.py
	│   ├── models
	│   │   └── __init__.py
	│   ├── services
	│   │   └── __init__.py
	│   ├── static
	│   │   └── __init__.py
	│   ├── templates
	│   │   └── __init__.py
	│   └── utils
	│       └── __init__.py
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

这里稍作介绍，首先是第一级目录的话，主要分为两类，一类是目录，另一类是运行相关的文件；其中目录有：

- application：项目所有逻辑代码都放这
- config：项目的配置文件，按不同环境各占一份
- deploy：部署相关的文件，后续将使用到
- tests：单元测试代码所在的目录

文件的话分别有：

- manage.py：Flask-Script 运行文件，后面介绍
- pylintrc：静态分析代码使用的 pylint 标准
- requirements.txt：项目依赖库的列表
- wsgi.py：wsgi 运行的文件

## 规范代码到指定目录

既然我们已经规定好了目录结构，是时候将我们的意面分到各个盘子里了。首先从文件开始，因为我们还没有介绍 Flask-Script，静态检查和 wsgi，所以就忽略这些文件，那么就剩下 requirements.txt 文件了。这个文件的内容都在我们的 《[本书概述](chapter001.md)》中列举了，直接放进去就好了。

	Flask==0.10.1
	flask-mongoengine==0.7.5
	Flask-Login==0.3.2
	Flask-Admin==1.4.0
	Flask-Redis==0.1.0
	Flask-WTF==0.12

然后是时候解耦代码了，我们没有表单，暂时没有 services，没有静态文件也没有页面模板，所以可以这样合并：

- 将 route 代码放到 application/controllers 中
- 将 model 代码放到 application/models 中
- 将初始化绑定 app 的代码放到 application/__init__.py 中
- 将 数据库等配置放到 config/development.py 中

最后就是编写 manager.py 文件了。这里概要得列举几个重要的文件，更多的文件大家可以从 github 上 clone 代码出来阅读。

## 合并后的文件

manager.py

	# coding: utf-8
	from flask.ext.script import Manager
	from application import create_app
	
	# Used by app debug & livereload
	PORT = 8080
	
	app = create_app()
	manager = Manager(app)
	
	
	@manager.command
	def run():
	    """Run app."""
	    app.run(port=PORT)
	
	
	if __name__ == "__main__":
	    manager.run()

application/__init__.py

	# coding: utf-8
	import sys
	import os
	
	# Insert project root path to sys.path
	project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
	if project_path not in sys.path:
	    sys.path.insert(0, project_path)
	
	import logging
	from flask import Flask
	from flask_wtf.csrf import CsrfProtect
	from config import load_config
	from application.extensions import db, login_manager
	from application.models import User
	from application.controllers import user_bp
	
	# convert python's encoding to utf8
	try:
	    reload(sys)
	    sys.setdefaultencoding('utf8')
	except (AttributeError, NameError):
	    pass
	
	
	def create_app():
	    """Create Flask app."""
	    config = load_config()
	    print config
	
	    app = Flask(__name__)
	    app.config.from_object(config)
	
	    if not hasattr(app, 'production'):
	        app.production = not app.debug and not app.testing
	
	    # CSRF protect
	    CsrfProtect(app)
	
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
	
	    login_manager.login_view = 'login'
	
	    @login_manager.user_loader
	    def load_user(user_id):
	        return User.objects(id=user_id).first()
	
	
	def register_blueprint(app):
	    app.register_blueprint(user_bp)

application/controllers/__init__.py

	#!/usr/bin/env python
	# encoding: utf-8
	import json
	
	from flask import Blueprint, request, jsonify
	from flask.ext.login import current_user, login_user, logout_user
	
	from application.models import User
	
	
	user_bp = Blueprint('user', __name__, url_prefix='')
	
	
	@user_bp.route('/login', methods=['POST'])
	def login():
	    info = json.loads(request.data)
	    username = info.get('username', 'guest')
	    password = info.get('password', '')
	
	    user = User.objects(name=username,
	                        password=password).first()
	    if user:
	        login_user(user)
	        return jsonify(user.to_json())
	    else:
	        return jsonify({"status": 401,
	                        "reason": "Username or Password Error"})
	
	
	@user_bp.route('/logout', methods=['POST'])
	def logout():
	    logout_user()
	    return jsonify(**{'result': 200,
	                      'data': {'message': 'logout success'}})

	@user_bp.route('/user_info', methods=['POST'])
	def user_info():
	    if current_user.is_authenticated:
	        resp = {"result": 200,
	                "data": current_user.to_json()}
	    else:
	        resp = {"result": 401,
	                "data": {"message": "user no login"}}
	    return jsonify(**resp)

config/development.py

	# coding: utf-8
	import os
	
	
	class DevelopmentConfig(object):
	    """Base config class."""
	    # Flask app config
	    DEBUG = False
	    TESTING = False
	    SECRET_KEY = "sample_key"
	
	    # Root path of project
	    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
	
	    # Site domain
	    SITE_TITLE = "twtf"
	    SITE_DOMAIN = "http://localhost:8080"
	
	    # MongoEngine config
	    MONGODB_SETTINGS = {
	        'db': 'the_way_to_flask',
	        'host': 'localhost',
	        'port': 27017
	    }

