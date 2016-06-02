# coding: utf-8
import os

from .default import Config


class DevelopmentConfig(Config):
    """Base config class."""
    # Flask app config
    DEBUG = False
    TESTING = False
    SECRET_KEY = "sample_key"

    # Root path of project
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Site domain
    SITE_TITLE = "twtf"
    SITE_DOMAIN = "http://localhost:8080"

    # MongoEngine config
    MONGODB_SETTINGS = {
        'db': 'the_way_to_flask',
        'host': '192.168.59.103',
        'port': 27017
    }
