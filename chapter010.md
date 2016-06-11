# 使用 Flask-Admin 管理数据库数据

我们回过头来看看我们到目前为止的 REST API，发现好像现在都不知道有多少条 User 记录了，甚至于连获取所有 User 记录的 API 都没提供，更别说随便查看用户的记录了。面对这个困境， Flask 的扩展是否还能给我们更多的惊喜呢？答案肯定还是可以的。这一章节，我将带读者认识一个 Flask 中的管理扩展 —— Flask-Admin。

使用 Flask-Admin，我们可以方便快捷得管理我们的 Model 数据，让我们能够省去一大堆开发管理系统的时间，而更多得将精力放到梳理业务逻辑之上，下面就开始讲解一下如何使用 Flask-Admin。

## 安装 Flask-Admin

没有什么特殊的，还是直接使用 pip 安装：

	pip install Flask-Admin==1.4.0

就直接安装上了 Flask-Admin 扩展，然后等待后续使用
 
## 初始化 Flsak-Admin

和其他常见扩展一般，Flask-Admin 还是需要和我们的 app 服务器绑定，所以还是老套路，但是，因为我们规范化了我们的目录结构，所以这里我们需要注意的是，创建 Flask-Admin 对象要放在 application/extensions.py 文件中，所以在我们的 application/extensions.py 中已经写入以下语句：

	from flask.ext.admin import Admin
	admin = Admin()
	
接下来就是要和我们的 Flask 服务器进行绑定了，还是老套路，不过还是因为规范化的原因，我们的绑定需要放到 **application/__init__.py** 中执行，那就需要在  **application/__init__.py** 文件中的 register_extensions 函数中添加以下语句：

	from application.extensions import admin
	
	admin.init_app(app)

然后就算完成了，接下来，我们运行服务器试试，此时我们运行服务器是使用以下语句了：

	python manage.py runserver
	
## 初见 Flask-Admin

当我们服务器跑起来之后，我们要想看到管理界面，只需要在浏览器中输入URL：

	http://localhost:5000/admin

你就能看到最简单的管理后台了，但是！！这里面什么都没有，就像这样：

![twtf_chapter010_001.png](https://ooo.0o0.ooo/2016/05/29/574ab443a9841.png)

看来第一印象不是很好，那么，我们要怎样才能看到东西？其实也不复杂，既然没有数据，那我们就将我们的数据 Model 加进去，怎么加，下面给出一个简单的例子，同样还是在 application/__init__.py 中：

	from flask_admin.contrib.mongoengine import ModelView
	
	from application.models import User, Role
	
	def register_extensions(app):
		admin.init_app(app)
		admin.add_view(ModelView(User))
    	admin.add_view(ModelView(Role))

这样就可以了，还是那样，重启一下我们的服务器再访问：

	http://localhost:5000/admin
	
这个时候，我们会发现有两个 Model 了：

![twtf_chapter010_002.png](https://ooo.0o0.ooo/2016/05/29/574ab739927e1.png)

## 操作 Flask-Admin

在后台中我们可以看到一些选项，例如List、Create、With select，然后这些选项下面是一个表格，也许你会发现这个表格是空的，那是因为你的数据库中没有数据，所以是空的很自然，那么我们要怎么添加数据呢？试试点一下 “Create” 看下：

![twtf_chapter010_003.png](https://ooo.0o0.ooo/2016/05/29/574ab85fce70a.png)

看到的是这个，我们填充完各个字段之后，点提交就能看到表格中有数据了。

![twtf_chapter010_004.png](https://ooo.0o0.ooo/2016/05/29/574ab8c1b38c9.png)

## 总结

本章很简约得介绍了 Flask 中的管理扩展 Flask-Admin，并且演示了如何添加管理我们的 Model 数据，并且简单得介绍了一下支持的操作，但是这些都只是皮毛，如果读者有兴趣的话，可以阅读我的文章[《Flask-Admin》](https://liuliqiang.info/flask-admin-turtorise/)了解更多知识，也可以查看 Flask-Admin 的[官方文档](https://flask-admin.readthedocs.io/en/latest/)学习关于 Flask-Admin 的内容。

