#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import logging
import logging.handlers
from datetime import datetime

from flask import Flask, current_app
from flask_admin.contrib.mongoengine import ModelView

from config import load_config
from application.extensions import db, login_manager, admin, jwt
from application.models import User, Role
from application.controllers import all_bp

# convert python's encoding to utf8
try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except (AttributeError, NameError):
    pass


def create_app(mode):
    """Create Flask app."""
    config = load_config(mode)

    app = Flask(__name__)
    app.config.from_object(config)

    if not hasattr(app, 'production'):
        app.production = not app.debug and not app.testing

    # Register components
    configure_logging(app)
    register_extensions(app)
    register_blueprint(app)

    return app


def register_extensions(app):
    """Register models."""
    db.init_app(app)
    login_manager.init_app(app)

    # flask-admin configs
    admin.init_app(app)
    admin.add_view(ModelView(User))
    admin.add_view(ModelView(Role))

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.objects(id=user_id).first()

    # jwt config
    def jwt_authenticate(username, password):
        logging.info("username:{}\npassword:{}\n".format(username, password))
        user = User.objects(name=username, password=password).first()
        return user

    def jwt_identity(payload):
        logging.info("payload:{}".format(payload))
        user_id = payload['identity']
        return User.objects(id=user_id).first()

    def make_payload(identity):
        iat = datetime.utcnow()
        exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
        nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA')
        identity = str(identity.id)
        return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': identity}

    jwt.authentication_handler(jwt_authenticate)
    jwt.identity_handler(jwt_identity)
    jwt.jwt_payload_handler(make_payload)

    jwt.init_app(app)


def register_blueprint(app):
    for bp in all_bp:
        app.register_blueprint(bp)


def configure_logging(app):
    logging.basicConfig()
    if app.config.get('TESTING'):
        app.logger.setLevel(logging.CRITICAL)
        return
    elif app.config.get('DEBUG'):
        app.logger.setLevel(logging.DEBUG)
        return

    app.logger.setLevel(logging.INFO)

    info_log = os.path.join("running-info.log")
    info_file_handler = logging.handlers.RotatingFileHandler(
        info_log, maxBytes=104857600, backupCount=10)
    info_file_handler.setLevel(logging.DEBUG)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)
