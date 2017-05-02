#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase

from application import create_app
from application.extensions import db


class TodoTest(TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()
        db.connection.drop_database('the_way_to_flask_test')

    def tearDown(self):
        self.ctx.pop()
