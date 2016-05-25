# 注册登录

在我们的前几章中，围绕着要讲解的内容持续得再丰富一个 REST 服务。但是，截止到目前为止，我们这个 REST 服务都是没有权限控制的，也就是说，如果将这个 REST 服务发布到外网上去，那么将可以被任何人操作，增删改查都不是问题。

作为我们的重要服务（真的很重要:-D），我们怎么能让别人随便操作我们的数据呢，所以这一章就讲解一下如何使用 Flask 的又一扩展 **Flask-Login** 来进行访问控制。

## 安装 Flask-Login

根据在 《[本书概述](chapter001.md)》中列举的那样，我们使用的 **Flask-Login **的版本是 

	Flask-Login==0.3.2

所以安装的话直接使用 pip 安装即可：
	
	pip install Flask-Login==0.3.2

## 初始化 Flask-Login

和我们在上一章使用 Flask-MongoEngine 一样，使用 Flask-Login 还是依赖于 Flask，所以我们还是需要和 app 这样服务器绑定起来，所以我们一开始还是需要这样和服务器绑定的：

	from flask.ext.login import LoginManager
	login_manager = LoginManager()
	login_manager.init_app(app)

这样就将 Flask-Login 和服务器绑定起来了。但是，这好像没有什么作用啊，我们要怎么登陆呢？Flask-Login 怎么才知道登录的 URL 的是哪个？怎么验证我们的账号密码？怎么才能知道登陆的用户是谁？这些都是关键的问题啊。

## 设置 Flask-Login

对于前面提到的问题，我们一一解决，解决完之后我们的 Flask-Login 就差不多算是会使用了。

首先是登陆的 URL 是什么？这个在 Flask-Login 中是没有默认的登陆 URL 的，所以需要我们指定：

	from flask.ext.login import login_user

	login_manager.login_view = 'login'

	@app.route('/login', methods=['POST'])
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

这里其实就做了两件事：

1. 指定了 login_view 为 'login'
2. 编写的登陆的代码逻辑

那我们来看第一点，指定 login_view，也就是告诉 Flask 我们的处理的登陆的 URL 是哪个。这里我们发现是 'login'，那么 Flask 是怎么根据 login 找到我们的登陆逻辑所在的位置的呢？这里除了 'login' 我们还能填写其他的字符串吗？

这里先给出答案，是不能的，也就是说，在我们这段代码中，必须指定为 'login'，这里的 'login' 的意思就是在当前文件找到 

	def login(self, xxx)

这个函数，然后它就是我们处理登陆逻辑代码所在的地方。

假如说我们处理登陆逻辑的代码没有放在这个文件，而是放在了其他文件，例如 auth.py 里面的 login 函数里面，那么我们就需要指定为：

	login_view = 'auth.login'

### 登陆逻辑

还是看回上一段代码，我们发现这是一个普通的 Flask 处理请求的函数，说普通在于：

- 从客户端的请求中获得参数，和之前的 CRUD 一样
- 无论是登陆成功还是失败都返回 json 串给客户端

那么凭什么这段代码就能胜任登陆用户的职责呢？问题的关键就在于 

	login_user(user)

这一句，仅仅是通过这简单的一句，就将当前用户的状态设置成已登录。这里不做过深入的讲解，只需要知道当这个函数被调用之后，用户的状态就是登陆状态了。

那现在问题是，下次有请求过来，我们怎么知道是不是有用户登陆了，怎么知道是哪个用户？这时我们就会发现我们的 Model 还不够完善，需要完善一下 Model。具体应该这样完善一下：

	class User(db.Document):   
	    name = db.StringField()
	    password = db.StringField()
	    email = db.StringField()                                                                                                 
	                              
	    def to_json(self):        
	        return {"name": self.name,
	                "email": self.email}
	                              
	    def is_authenticated(self):
	        return True

	    def is_active(self):   
	        return True           
	                              
	    def is_anonymous(self):
	        return False          
	                              
	    def get_id(self):         
	        return str(self.id)

我们可以看到，这里增加了两个方法，分别是：
	
- is_authenticated：当前用户是否被授权，因为我们登陆了就可以操作，所以默认都是被授权的
- is_anonymous: 用于判断当前用户是否是匿名用户，很明显，如果这个用户登陆了，就必须不是
- is_active： 用于判断当前用户是否已经激活，已经激活的用户才能登陆
- get_id： 获取改用户的唯一标示

这里，我们仅仅可以通过 is_authenticated 来判断用户时候有权限操作我们的 API，但是，我们还不能知道当前的登陆用户是谁，所以我们还需要告诉 Flask-Login 如何通过一个 id 获取到用户的方法：

	@login_manager.user_loader
	def load_user(user_id):
	    return User.objects(id=user_id).first()

通过指定 user_loader，我们就可以查询到当前的登陆用户是谁了。这样我们就将登陆、判断用户是否登陆都完善起来了。

## 登陆可见

既然都登陆了，我们就需要控制登陆的权限了，我们设置增加、删除和修改的 REST API 为登陆才能使用，唯有查询的 API 才能随便可见。

控制登陆可用的方法比较简单，只需要加一个 login_required 的装饰器即可。我们还是以之前那些章节的 REST DEMO 为例进行改写：

	from flask.ext.login import login_required

	@app.route('/', methods=['PUT'])      
	@login_required                       
	def create_record(): 
		......
	
	@app.route('/', methods=['POST'])                                                                                            
	@login_required
	def update_record():
		......
	
	@app.route('/', methods=['DELETE'])
	@login_required
	def delte_record():
		......

这样我们就限制了增加、修改和删除操作必须登陆用户才能操作，而我们也能记录是哪个用户做的操作了。

## 用户信息

既然服务器提供了登陆的支持，那么肯定少不了退出登陆的支持；同时，作为客户端，可能关注的是想知道到底有没有登陆？

对于退出登陆，很简单，都根本不需要使用到 User 的这个 Model 了。代码如下：
	
	from flask.ext.login import logout_user
	
	@app.route('/logout', methods=['POST'])
	def logout():
	    logout_user()
	    return jsonify(**{'result': 200,
	                      'data': {'message': 'logout success'}})

这里就调用了一个  `logout_user` 的方法就退出了登陆。

然而即使退出了登陆客户端也不知道，除非尝试请求一下新增、修改或者删除的操作，发现无法操作了，这时就知道了我已经退出登陆了，这样明显不合理！所以，这里再增加一个获取当前登陆用户信息的接口：

	from flask.ext.login import current_user

	@app.route('/user_info', methods=['POST'])
	def user_info():
	    if current_user.is_authenticated:
	        resp = {"result": 200,
	                "data": current_user.to_json()}
	    else:                                                                                                                    
	        resp = {"result": 401,
	                "data": {"message": "user no login"}}
	    return jsonify(**resp)

这里一个重要的点就是第一句，这里有一个成员叫做 `current_user`，这个变量表示的是当前请求的登陆用户，如果登陆了，那么它就是我们设置的 Model User 的对象，根据我们的 Model 定义， is_authenticated 一直为 True，表示登陆了；如果没有登陆，那么它就是默认的匿名用户 AnonymousUserMixin 的对象，is_authenticated 就为 False，就表示没有登陆。

如果登陆的话，那么 current_user 就是 User 的对象了，那么 to_json 方法就可以返回当前登陆用户的用户信息了，这样的话，我们就可以编写获取用户信息的 API 了。

本章的完整代码为：

	#!/usr/bin/env python
	# encoding: utf-8
	import json
	from flask import Flask, request, jsonify
	from flask.ext.login import (current_user, LoginManager,
	                             login_user, logout_user,
	                             login_required)
	from flask_mongoengine import MongoEngine
	
	
	app = Flask(__name__)
	app.config['MONGODB_SETTINGS'] = {
	    'db': 'the_way_to_flask',
	    'host': 'localhost',
	    'port': 27017
	}
	app.secret_key = 'youdontknowme'
	
	db = MongoEngine()
	login_manager = LoginManager()
	db.init_app(app)
	login_manager.init_app(app)
	
	
	login_manager.login_view = 'login'
	
	
	@login_manager.user_loader
	def load_user(user_id):
	    return User.objects(id=user_id).first()
	
	
	@app.route('/login', methods=['POST'])
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
	
	
	@app.route('/logout', methods=['POST'])
	def logout():
	    logout_user()
	    return jsonify(**{'result': 200,
	                      'data': {'message': 'logout success'}})
	
	
	@app.route('/user_info', methods=['POST'])
	def user_info():
	    if current_user.is_authenticated:
	        resp = {"result": 200,
	                "data": current_user.to_json()}
	    else:
	        resp = {"result": 401,
	                "data": {"message": "user no login"}}
	    return jsonify(**resp)
	
	
	class User(db.Document):
	    name = db.StringField()
	    password = db.StringField()
	    email = db.StringField()
	
	    def to_json(self):
	        return {"name": self.name,
	                "email": self.email}
	
	    def is_authenticated(self):
	        return True
	
	    def is_active(self):
	        return True
	
	    def is_anonymous(self):
	        return False
	
	    def get_id(self):
	        return str(self.id)
	
	
	@app.route('/', methods=['GET'])
	def query_records():
	    name = request.args.get('name')
	    user = User.objects(name=name).first()
	
	    if not user:
	        return jsonify({'error': 'data not found'})
	    else:
	        return jsonify(user.to_json())
	
	
	@app.route('/', methods=['PUT'])
	@login_required
	def create_record():
	    record = json.loads(request.data)
	    user = User(name=record['name'],
	                password=record['password'],
	                email=record['email'])
	    user.save()
	    return jsonify(user.to_json())
	
	
	@app.route('/', methods=['POST'])
	@login_required
	def update_record():
	    record = json.loads(request.data)
	    user = User.objects(name=record['name']).first()
	    if not user:
	        return jsonify({'error': 'data not found'})
	    else:
	        user.update(email=record['email'],
	                    password=record['password'])
	    return jsonify(user.to_json())
	
	
	@app.route('/', methods=['DELETE'])
	@login_required
	def delte_record():
	    record = json.loads(request.data)
	    user = User.objects(name=record['name']).first()
	    if not user:
	        return jsonify({'error': 'data not found'})
	    else:
	        user.delete()
	    return jsonify(user.to_json())
	
	
	if __name__ == "__main__":
	    app.run(port=8080, debug=True)