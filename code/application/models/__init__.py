#!/usr/bin/env python
# encoding: utf-8
from application.extensions import db


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
    role = db.ReferenceField('Role')

    def to_json(self):
        return {"name": self.name,
                "email": self.email,
                "role": self.role.name}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
