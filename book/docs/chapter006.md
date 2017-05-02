# 自建装饰器实现权限控制

在上一章 [《登陆注册》](chapter005.md)中，我们为 REST 的 API 设置了新增、更新和删除的操作需要登陆才能完成。细想一下，这样未免太过草率，因为对于一个系统来说，用户肯定是分为不同的级别的，例如普通的用户也就只能查查数据，然后一些用户还能多一个增加数据的权限，再高级一点的还能修改数据，最高级的就是增删改查都能。

对于这些更加丰富的需求，我们目前的登陆可用明显还不能满足需求，因此，按常规本章应该会引入一个新的扩展，而 Flask 确实是有一款叫做 `Flask-Principal`，的扩展可以满足我们的需求，通过这个扩展，我们希望能够达到更细粒度得控制用户的权限。但是，我**嫌弃这个扩展太累赘**了，所以本章不准备使用这个扩展，而是自己编写一个权限控制的扩展进行权限的控制。

## 权限控制设计

我们这里的权限控制采用 [RBAC](https://en.wikipedia.org/wiki/Role-based_access_control) 的方式，首先，我们会创建一个 Role 的 Model，然后给每个 User 分配一个 Role，这样的话，我们就可以限制某个操作需要某种 Role 才能执行，这样的话就实现了更细粒度的权限控制。

这里还有个实现细节需要先说明一下，我们的 Role 的权限是以二进制位来表示的，每一个二进制位表示一种权限：

- 第一位表示可以读取记录
- 第二位表示可以新建记录
- 第三位表示可以更新记录
- 第四位表示可以删除记录

这样的话，如果一个用户只能读取记录，那么他对应的 Role 的权限应该是 **0000 0001b** ，换算成十六进制的话就是： 0x01

如果一个用户所有操作都可以执行，那么它的权限应该对应于 **0000 1111b**，换算成十六进制的话就是：0x0f 

那么，假如我们要判断一个用户时候可以进行新建操作，那么应该怎么实现这个逻辑？我这里的实现机制是如果是只有新建操作，那么对应的权限就是：**0000 0010b**，那如果我要判断一个用户时候有新建的权限，那么我只需要对这个**用户的权限**和这个操作所**需要的权限**进行 **and 操作**，如果得到的结果等于需要的权限的话，那么就表示该用户拥有权限，可能说得有点复杂，上一个简单的例子

	用户 A 的权限：      0000 0001b      只有读取记录的权限
	用户 B 的权限：      0000 1111b      拥有所有权限
	新建记录需要权限：    0000 0010b      需要新建权限
	用户A是否可以新建：   0000 0001b and 0000 0010b = 0000 0000b ！= 新建权限，所以不能新建
	用户B时候可以新建：   0000 1111b and 0000 0010b = 0000 0010b  == 新建权限，所以可以新建
 
大概就是这样一个场景，大家可以自己动手演练演练，看下是否可行。

## 创建 Role Model

之前已经在 [《集成数据库》](chapter004.md) 章节中讲解过了如何创建 Model，所以这里直接根据之前的经验创建 Role Model，然后再往 User 中加上一个 Role 字段。

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
	    role = db.ReferenceField('Role'， default=DEFAULT_ROLE)

这里就简单得创建了一个 Role 的 Model，而 Role 只有一个名称，用于标示这个角色，另外一个就是该角色拥有的权限了。然后就是在 User 中添加了一个 ReferenceField，这个在 MongoEngine 里面就表示是外引用的意思，我们可以直接通过这个成员变量访问到用户的 Role 的 permission。

同时，为了保持代码的可维护性，我们将 permission 都写在一个类中，还设置了一个默认的权限，默认为 READ。

因为我们现在的数据库中还没有 Role 相关的记录，所以我们需要在启动应用的时候进行插入数据，所以我做了这样的一个操作：

	# init roles     
	if Role.objects.count() <= 0:  
	    READ_ROLE = Role('READER', Permission.READ)
	    CREATE_ROLE = Role('CREATER', Permission.CREATE)
	    UPDATE_ROLE = Role('UPDATER', Permission.UPDATE)
	    DELETE_ROLE = Role('DELETER', Permission.DELETE)
	    DEFAULT_ROLE = Role('DEFAULT', Permission.DEFAULT)

	    READ_ROLE.save()
	    CREATE_ROLE.save()
	    UPDATE_ROLE.save()
	    DELETE_ROLE.save()
	    DEFAULT_ROLE.save()
	else:            
	    READ_ROLE = Role.objects(permission=Permission.READ).first()
	    CREATE_ROLE = Role.objects(permission=Permission.CREATE).first()
	    UPDATE_ROLE = Role.objects(permission=Permission.UPDATE).first()
	    DELETE_ROLE = Role.objects(permission=Permission.DELETE).first()
	    DEFAULT_ROLE = Role.objects(permission=Permission.DEFAULT).first()

虽然这段代码有不严谨的地方，但是作为讲解的话无关大雅，通过这段代码，我们可以保证在下面的代码中我们有五种 Role 的对象，分别对应着增删改查，还有一个默认的角色，他为读取权限。同时，我们也应该修改一下我们的 API，让他能够增加用户的默认权限。

	@app.route('/', methods=['POST'])
	@login_required 
	def create_record():
	    record = json.loads(request.data)
	    user = User(name=record['name'],
	                password=record['password'],
	                email=record['email'],
	                role=DEFAULT_ROLE)
	    user.save() 
	    return jsonify(user.to_json())

这段代码只增加了一行，就是：

	role=DEFAULT_ROLE

## 权限控制

好，到这里算是完成了一半了，我们的角色已经算是有了，然后就是怎么进行权限控制了，我希望权限控制代码能够竟可能得简单，最好是能用装饰器实现，对于一些默认权限就能访问的，我希望不用加权限控制的代码就好了。没有不能实现的需求，只是实现得好坏而已，所以，既然我们都能描述出需求，那么就能够写出满足需求的代码。

首先，我们是需要编写一个权限控制的[装饰器](https://liuliqiang.info/python-decorator-description/)的，我们希望这个[装饰器](https://liuliqiang.info/python-decorator-description/)可以很方便得进行权限控制，最好是可以这样：

	@creater_required()
	def create_model():
		... ...

或者这样也可以接受：

	@permission_required(CREATE_PERMISSION):
	def create_model():
		... ...

那么，就先写一个较为简单的版本试试先：

	def permission_required(permission):
	    def decorator(func):           
	        @wraps(func)               
	        def decorated_function(*args, **kwargs):
				if not current_user.is_authenticated:
					abort(401) 
	            user_permission = current_user.role.permission
	            if user_permission & permission == permission:
	                return func(*args, **kwargs)
	            else:                  
	                abort(403)         
	        return decorated_function
	    return decorator

这一版本我们可以简单得看这几句关键的代码：

	if not current_user.is_authenticated:
		abort(401) 
    user_permission = current_user.role.permission
    if user_permission & permission == permission:
        return func(*args, **kwargs)
    else:                  
        abort(403) 

首先用户没有登陆肯定是没有权限的了，所以返回 401 未授权错误，如果用户没有权限（权限设计中的描述），那么就返回 403 禁止访问。

接着我们就在我们的 REST API 中尝试一下这个权限，这里相对新增用户进行尝试：

	@app.route('/', methods=['POST'])
	@permission_required(Permission.CREATE)   
	def create_record():               
	    record = json.loads(request.data) 
	    user = User(name=record['name'],  
	                password=record['password'],
	                email=record['email'],
	                role=DEFAULT_ROLE)  
	    user.save()                     
	    return jsonify(user.to_json()

这里只将 `@login_required` 的装饰器换成了

	@permission_required(Permission.CREATE)

然后我们尝试一下新建记录：

	POST http://localhost:8080
	
	{
	  "email": "liqianglau@outlook.com",
	  "name": "tyrael",
	  "password": "password"
	}

然后发现响应是：

![Image-2016-05-26-020312001.png](https://ooo.0o0.ooo/2016/05/25/5745ea1c6bd61.png)

说明我们的权限控制生效啦。


