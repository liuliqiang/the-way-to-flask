# 使用 Gunicorn 和 Nginx 部署 Flask 项目

在实际的生产环境中，我们很少是直接使用命令：

	python app.py
	
运行 Flask 应用提供服务的，正常都会集成 WSGI Web服务器提供服务，而在众多的 WSGI Web 服务器中，比较常用的主要有两种，分别是 Gunicorn 和 UWSGI，同时，我们也会使用 Nginx 作为反向代理进行部署应用。

本文因为需要安装 Nginx，所以文章内的命令和使用的系统相关，但是这样的命令不多，本文使用的 **Ubuntu 16.04**，因此包管理软件是 **apt**，如果使用的 RedHat 系列的话，那完全可以用 **yum** 代替。其他系列的系统可以查找相关文档寻找代替管理工具。

## 安装组件

	sudo apt-get update
	sudo apt-get install python-pip python-dev nginx
	
	pip install gunicorn 
	pip install flask

这里前两句是更新一下软件源，并且保证我们的 pip 和 python 依赖库已经安装上了，同时，别忘了安装反向代理 Nginx。后面两句就是安装我们必备的 Gunicorn 和 Flask Python 库了。

## 下载代码

因为在我们的前文中已经写了一个代码了，所以这里就继续使用这段代码，使用方式是：
	
	git clone git@github.com:luke0922/the-way-to-flask.git
	cd the-way-to-flask/code
	pip install -r requirements.txt
	python manage.py runserver
	
此时，我们的服务器应该是已经运行起来了，但是，默认 Ubuntu 是开启了防火墙屏蔽所有端口访问的，所以我们可能需要打开防火墙端口，在 Ubuntu 16.04 中可以这样做：

	sudo ufw allow 5000

现在，应该可以访问我们的应用了，在命令行上我们敲一下这个命令，访问以下 WEB 服务：

	http://localhost:5000

一切正常的话，

## 创建 WSGI 切入点


	vim wsgi.py
	
里面内容填：

	from myproject import app
	
	if __name__ == "__main__":
	    app.run()

然后使用这个命令运行代码：

	gunicorn --bind 0.0.0.0:5000 wsgi:app

依旧访问这个地址看看：

	http://localhost:5000

## 常见 systemd Unit File

	vim /etc/systemd/system/app.service
	
里面的内容写：

	[Unit]
	Description=Gunicorn instance to serve myproject
	After=network.target
	
	[Service]
	User=www
	Group=www
	WorkingDirectory=/home/www/myproject
	Environment="PATH=/home/www/myproject/myprojectenv/bin"
	ExecStart=/home/www/myproject/myprojectenv/bin/gunicorn --workers 3 --bind unix:myproject.sock -m 007 wsgi:app
	
	[Install]
	WantedBy=multi-user.target
	
保存退出，然后尝试一下命令：

	sudo systemctl start app
	sudo systemctl enable app

## 配置 Nginx

配置Nginx

	sudo nano /etc/nginx/sites-available/myproject

里面写：

	server {
	    listen 80;
	    server_name server_domain_or_IP;
	    
	     location / {
	        include proxy_params;
	        proxy_pass http://unix:/home/sammy/myproject/myproject.sock;
	    }
	}
	
保存之后，用 nginx 自带工具验证一遍

	nginx -t
	
如果ok的话然后让 nginx 重新加载配置

	nginx -s reload
	
关闭服务器端口：

- sudo ufw delete allow 5000
- sudo ufw allow 'Nginx Full'

此时访问服务器试试：

	http://192.168.59.103





