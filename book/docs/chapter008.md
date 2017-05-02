# 建立目录管理配置

在前面一章[《更好得维护代码》](chapter007.md) 中，我们将项目按照功能作用划分到不同的目录中，这样使得我们的项目结构更加清晰和规整了。但是，因为上一章节的内容比较多，如果作为初学者来说，肯定是有好多有疑问的地方，从本章开始都会进行介绍，让大家对 Flask 的使用更加得得心应手。

本章主要介绍的是 Flask 中的配置管理，从前面章节[《更好得维护代码》](chapter007.md) 里，可以发现，配置目录 **config** 下包含多个配置文件，为什么要包含这么多文件，而我们要如何处理这些配置文件，都是本章的讲解内容。

	├── config
	│   ├── __init__.py
	│   ├── default.py
	│   ├── development.py
	│   ├── development_sample.py
	│   ├── production.py
	│   ├── production_sample.py
	│   └── testing.py

## 环境分类

有一个重要的概念是需要我们关注的，那就是**每个配置文件都是与环境相关的**，也就是说，就是因为有多个环境，所以才会出现多个配置。如果不太理解这句话的意思的话，我们看一下 config 目录下的文件名，其实可以分为几类：

- development： 开发环境，一般为本地开发环境使用
- production：生产环境，一般为线上部署运行环境使用
- testing： 测试环境，一般用于各种测试使用

如我们所看到的一样，我们在平时的工作中会有各种环境，我们在本地开发调试的时候应该有个本地环境，当我们转测试之后后会有个测试环境，测试完成之后放到线上之后会有个线上正式环境，而每个环境很难保持配置完全一致，所谓的不一致是指例如数据库信息、程序运行的模型等，例如我们本地的开发环境数据库地址是：

	MongoDB：
    version：3.2.6
    ip：localhost
    port：27017

而在生产环境却是：

	MongoDB：
	    version：3.2.6
	    ip：192.168.59.104
	    port：27017

所以为了方便开发、测试和部署，我们就会设置多份配置文件，这样就可以快速得在不同环境中运行。如果你有其他的情况，可以随时添加配置文件，完全没问题。

## 加载配置

那这么多份配置文件，我如何让程序制定加载哪份配置文件呢？这里的奥妙就在 **`config/__init__.py`** 文件中。我们打开这个文件看看：

	# coding: UTF-8
	import os
	
	
	def load_config(mode=os.environ.get('MODE')):
	    """Load config."""
	    try:
	        if mode == 'PRODUCTION':
	            from .production import ProductionConfig
	            return ProductionConfig
	        elif mode == 'TESTING':
	            from .testing import TestingConfig
	            return TestingConfig
	        else:
	            from .development import DevelopmentConfig
	            return DevelopmentConfig
	    except ImportError:
	        from .default import Config
	        return Config

在 config/__init__.py 文件中，我定义了一个 load_config 函数，这个函数接受一个 `mode` 参数，表示是获取什么环境的配置，如果不传这个参数的话，那默认使用的就是系统环境变量中的 `MODE` 环境变量，然后就根据指定的环境返回指定的配置文件。

如果没有指定的配置文件的话，那么就只能返回默认环境变量了。同样的，如果你需要新增自定义的环境配置文件，那么只需要简单得修改这个函数，并且指定加载你自定义的配置文件即可。

## 使用配置

加载配置这一问题解决之后，接下来就是在我们的 Flask 应用中使用这些配置了，既然都 load 好了配置，那么使用也就问题不大了，这里是一个示例：

    """Create Flask app."""
    config = load_config(mode)

    app = Flask(__name__)
    app.config.from_object(config)
    
这里首先将配置 load 出来，然后使用 Flask 对象的 config.from_object 设置配置。就这么简单。

## 总结

本章对 Flask 中如何配置多环境的配置文件进行了说明和介绍，然后分析了如何加载不同配置文件的原理，最后，给出了一个如何在实际应用中使用配置的示例。    


