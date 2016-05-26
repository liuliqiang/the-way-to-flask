#!/usr/bin/env python
# encoding: utf-8

from flask.ext.mongoengine import MongoEngine
db = MongoEngine()

from flask.ext.login import LoginManager
login_manager = LoginManager()
