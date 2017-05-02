# 使用 Flask-MongoEngine 集成数据库

在前面一章 [简单的 REST 服务](./chapter003.md) 中，我们的数据都是保存在文件中的，我们可以发现，这样很是繁琐，每个请求中都需要进行读取文件，写出文件的操作，虽然显然我们可以对文件操作进行一个封装，但是，毕竟是文件存储，数据稍微多一点查询等操作必然时间变长。

面对这样的一个问题，这里引入了对数据库的依赖，在我们的 [本书概述](./chapter001.md) 中，我介绍了数据库的版本信息，本章使用的是 MongoDB，具体的版本还有数据库地址信息为：

	version：3.2.6
	ip：localhost
	port：27017

## 创建数据模型

既然我们想使用数据库来保存数据，我们可以使用原生的 pymongo 来操作 MongoDB，但是，我们这里为了更进一步得简化我们的操作，所以我们需要创建数据模型。

数据模型主要的功能是用于说明我们的数据包含哪些字段，每个字段分别是什么类型，有什么属性（唯一的，还是固定几个值中的一个）等等。这样可以帮助我们在操作数据的时候可以时刻很清晰得知道我们的数据的信息，即使我们不看数据库中的数据。

这里我们要介绍的操作 MongoDB 的 Flask 扩展是 Flask-MongoEngine，这个扩展是 MongoEngine 在 Flask 上的扩展，也就是说，我们完全可以独立使用 MongoEngine 而不依赖于 Flask，但依不依赖相差不多，我个人觉得最大的区别在于配置如何处置，所以这里使用依赖 Flask 的扩展。

要在 Flask 中使用 MongoEngine，首先我们需要先在 Flask 中配置 MongoDB 的信息，然后再使用我们的服务器初始化 MongoEngine，这样我们就将数据库和服务器建立了联系，这个在代码中可以这样来表示：

	app.config['MONGODB_SETTINGS'] = {
	    'db': 'the_way_to_flask',
	    'host': 'localhost',
	    'port': 27017
	}

	db = MongoEngine()
	db.init_app(app)

建立联系之后，我们就可以使用 MongoEngine 创建数据模型了。

我们这里还是继承上一章中的数据模型，也就是只有两个字段，分别是 name 和 email：

	class User(db.Document):
		name = db.StringField()
		email = db.StringField()

这样，我们的数据模型创建好了，整段完整的代码是：

	#!/usr/bin/env python
	# encoding: utf-8
	from flask import Flask
	from flask_mongoengine import MongoEngine
	
	
	app = Flask(__name__)
	app.config['MONGODB_SETTINGS'] = {
	    'db': 'the_way_to_flask',
	    'host': 'localhost',
	    'port': 27017
	}
	
	db = MongoEngine()
	db.init_app(app)
	
	
	class User(db.Document):
	    name = db.StringField()
	    email = db.StringField()
	
	
	if __name__ == "__main__":
	    app.run(debug=True)

## 操作数据

现在我们已经有数据模型(Model)和数据库关联起来了，那光有关联没用啊，我们没办法操作啊。接下来的内容就是讲解如何通过 Model 对数据库中的数据进行增删改查。


### 查询
MongoEngine 的增删改查非常简单，例如查询，我们可以使用：

	User.objects(name="zhangsan").first()

这个语句就将数据库中名字为 zhangsan 的用户查询出来了。我们来分析一下这个语句是怎么查询的。

首先是 `User.objects`，这里的 `User` 我们已经知道了是我们的 Model，那既然 User 都已经是 Model 了为什么还要 objects 呢？

就是因为 User 是 Model，因为 Model 本身只代表数据结构，那和我们查询有什么关系呢？所以这里引入了一个 objects 属性，表示一个查询集，这个集合默认就表示 User 表中的所有数据，所以我们后面的 `name=“zhangsan”` 就有点好理解了，其实就是从 User 表中的所有数据中过滤出 name 的值为 zhangsan 的记录，别忘了，过滤出来的数据是一个集合，而不是一个 User 对象，所以我们后面还加了一个 `first` 获取这个集合的第一个元素。

这样，我们就查询到了一个 User 对象。

### 新增

增加新记录就更简单了，例如我想插入一个 **name** 为 `lisi`，**email** 为 `lisi@gmail.com` 的用户，那么我们可以这样写：

	User(name='lisi', email='lisi@gmail.com').save()

就这么简单，首先，我们想创建了一个 User 对象，然后调用 save 方法就可以了。

### 删除

考虑一下如果我们要删除一个记录，我们是不是需要先找到这个需要删除的记录？在 MongoEngine 中就是这样的，如果我们要删除一个记录，我们想找到它，使用的是查询：

	user = User.objects(name="zhangsan").first()

找到之后，很简单，只需调用 delete 方法即可：

	user.delete()

这样，我们就将 zhangsan 这个用户删除掉了。

### 更新

和删除一样，如果我们需要更新一条记录，那么我们也先需要找到他，假设我们需要更新 lisi 的邮箱为： lisi@outlook.com，那么我们可以这么写：

	user = User.objects(name="zhangsan").first()
	user.update(email="lisi@outlook.com")

第一句还是查询啦，第二句这里使用了 update 方法，直接将需要修改的属性以及改变后的值作为参数传入，即可完成更新操作。

### 完整代码

这样，我们就知道了如何利用模型进行增删改查，那么我们就将这个知识都应用到我们的 REST 服务中，改写后的代码如下：

	#!/usr/bin/env python
	# encoding: utf-8
	import json
	from flask import Flask, request, jsonify
	from flask_mongoengine import MongoEngine
	
	
	app = Flask(__name__)
	app.config['MONGODB_SETTINGS'] = {
	    'db': 'the_way_to_flask',
	    'host': 'localhost',
	    'port': 27017
	}
	
	db = MongoEngine()
	db.init_app(app)
	
	
	class User(db.Document):
	    name = db.StringField()
	    email = db.StringField()
	
	    def to_json(self):
	        return {"name": self.name,
	                "email": self.email}
	
	
	@app.route('/', methods=['GET'])
	def query_records():
	    name = request.args.get('name')
	    user = User.objects(name=name).first()
	
	    if not user:
	        return jsonify({'error': 'data not found'})
	    else:
	        return jsonify(user.to_json())
	
	
	@app.route('/', methods=['PUT'])
	def create_record():
	    record = json.loads(request.data)
	    user = User(name=record['name'],
	                email=record['email'])
	    user.save()
	    return jsonify(user.to_json())
	
	
	@app.route('/', methods=['POST'])
	def update_record():
	    record = json.loads(request.data)
	    user = User.objects(name=record['name']).first()
	    if not user:
	        return jsonify({'error': 'data not found'})
	    else:
	        user.update(email=record['email'])
	    return jsonify(user.to_json())
	
	
	@app.route('/', methods=['DELETE'])
	def delte_record():
	    record = json.loads(request.data)
	    user = User.objects(name=record['name']).first()
	    if not user:
	        return jsonify({'error': 'data not found'})
	    else:
	        user.delete()
	    return jsonify(user.to_json())
	
	
	if __name__ == "__main__":
	    app.run(debug=True)

CRUD 使用的基本上都是我们介绍的方法，大家可以自己尝试得编写一些。