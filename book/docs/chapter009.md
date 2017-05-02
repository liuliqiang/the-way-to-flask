# 使用 Flask-Script 启动应用

看到这章的内容也许你会有疑惑，启动应用？不是很简单吗？我直接使用 

	python app.py

不就将应用跑起来了吗，而且我还能看到访问的日志呢。是的，没错，直接运行代码是可以将我们编写的 Web 应用跑起来，而且还能很好得查看运行信息，但是，假设你想更换配置呢？例如，你有 development1.py 和 development2.py 两个配置文件，一开始你使用 development1.py 运行，然后你想换成 development2.py 这个配置文件，那么你需要怎么做？根据我们在[《配置管理》](chapter008.md)中介绍的那样，你有两个选择，分别是：

- 修改系统变量 MODE
- 修改代码，直接指定 create_app('development1') => create_app('development2')

看上去都不是很方便，因为这至少涉及到两个动作，第一个是修改模式，第二个是启动应用。那么这个时候，假如我们在运行应用的时候能够指定需要使用的配置文件的话，那不是方便多了，例如：

	python app.py development1

这样的话，好像就好多了，确实，这样确实满足了我们的需求，但是，这仅仅满足了一个需求，那万一我们还想看我们的应用对外暴露的 API 有哪些呢？我还想使用我们应用的 python shell 呢？这些都是比较难实现的。然而，作为一个提供丰富扩展的框架，Flask 的贡献者们也已经为我们想到了，并且给我们提供了一个扩展 Flask-Script，可以让我们从这些繁琐的事情中解放出来。

可能机智的你已经发现了，在我们的[《更好得维护代码》](chapter007.md)中已经根目录里面多了一个 manage.py 的文件，是的，这个文件就是为使用 Flask-Script 而创建的，而我们启动应用也将使用这个文件。下面就来介绍一下 Flask-Script 的一些知识。

## 安装 Flask-Script

依旧还是老套路，直接使用 pip 安装既可。

	pip install Flask-Script

## 小试身手

和我们之前使用过的 Flask 扩展不一样，Flask-Script 不需要获取我们 app 的配置信息，所以就不用使用 init_app 这样的初始化操作了，但是，毕竟 app 是我们的 Flask 服务器，所以还是需要使用到它，所以我们一开始的启动脚本可以这样写：

	# coding: utf-8
	from flask_script import Manager
	from application import create_app
	
	app = create_app('development')
	manager = Manager(app)
	
	
	if __name__ == "__main__":
	    manager.run()

我们这就做了两个操作，分别是：

	manager = Manager(app)
	manager.run()

很奇怪的是，和我们最开始的运行的相比，好像更复杂了，因为我们最初的版本直接这样跑就可以了：

	app.run()
	
那为什么要多一个 manager 呢？因为manager 可以做更多的操作，例如指定运行参数，查看所有 API 等。

## 指定运行参数

如果我们想指定配置文件，Flask-Script 提供了一个 -c 的参数，然后可以这样做：

	#!/usr/bin/env python
	# encoding: utf-8
	from flask_script import Manager
	from application import create_app
	
	manager = Manager(create_app)
	manager.add_option('-c', '--config', dest='mode', required=False)
	
	
	if __name__ == "__main__":
	    manager.run()

其实这里做的改变就是不直接创建 app，而是将创建方法直接传给 Manager，然后多了重要的一行，那就是：

	manager.add_option('-c', '--config', dest='mode', required=False)

通过名字可以发现这是一个添加选项的语句，默认就是给我们的 create_app 添加参数选项，然后我们看一下它的参数分别有哪些：

- -c : 运行参数的简写
- --config : 运行参数的全写
- dest : 传递给 create_app 的参数名字，因为我们是 create_app(mode) ，所以这里是 'mode'
- required : 是否是必须的，这里因为有默认的 mode ，所以不需要必选。

就这样我们就可以给 create_app 传递参数了，那怎么传，这样子：

	python manage.py -c development  # 开发环境运行
	python manage.py -c testing      # 测试环境运行
	
就是这么简单，我们就可以在执行得时候指定要运行的环境了。

## 查看所有暴露的 API

很多时候，因为我们的项目是多人开发，所以我们经常会不知道我们的代码暴露了哪些 API。事实上，这在多人协作的项目中是非常常见的问题，例如我经历过的两个企业，其中一家是世界500强的 IT 企业，都存在这个问题，而他们的解决方法就是使用一份 Excel 管理暴露的接口，而这些接口都由各个模块的负责人自己填写，当然，后面我开发了一个统一管理系统对 API 进行管理，但毕竟在大的企业中，很难协调好所有的部门和产品，所以还是很难有全局的视角。

但是，在 Flask 中，我们就不需要担心有这种问题了，因为我们的 Flask-Script 还是提供了一个命令可以快速得帮助我们列举出我们的公开接口，使用上也很简单，直接这样写即可：

	from flask_script.commands import ShowUrls
	
	manager.add_command("showurls", ShowUrls())
	
然后，我们在控制台上敲以下命令：

	python manage.py showurls
	
你很惊喜得会发现这些输出：

	Rule                     Endpoint
	---------------------------------------
	/login                   user.login
	/logout                  user.logout
	/static/<path:filename>  static
	/user_info               user.user_info

它将我们所有的公开接口都打印出来了，但是，可能你也发现了，不完善的地方就是这里只给出了 URI，并没有给出请求方法，例如 GET、POST 等。这是有待提高的地方。

## 总结

本章介绍了 Flask-Script 这一扩展的使用，并且介绍了两个用法，分别是使用指定参数启动应用以及查看所有暴露出来的 API URI，但是也许你会有一些新的想法，但是 Flask-Script 并没有提供给你，没关系，Flask 作为一个对扩展友好的框架，你有任何想法都可以通过扩展来实现，更多的详情读者可以参考[Flask-Script官方文档](https://flask-script.readthedocs.io/en/latest/)来实现。

