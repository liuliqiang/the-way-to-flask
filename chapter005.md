# 保护你的 API

在我们的前几章中，围绕着要讲解的内容持续得再丰富一个 REST 服务。但是，截止到目前为止，我们这个 REST 服务都是没有权限控制的，也就是说，如果将这个 REST 服务发布到外网上去，那么将可以被任何人操作，增删改查都不是问题。

作为我们的重要服务（真的很重要:-D），我们怎么能让别人随便操作我们的数据呢，所以这一章就讲解一下如何使用 Flask 的又一扩展 **Flask-Login** 来进行访问控制。

## 安装 Flask-Login

根据我们在 《[本书概述](chapter001.md)》中列举的那样，我们使用的 **Flask-Login **的版本是 

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


登陆逻辑
