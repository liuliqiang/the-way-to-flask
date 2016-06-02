#!/usr/bin/env python
# encoding: utf-8
from application.extensions import db

__all__ = ['Role', 'User']


class Permission:
    READ = 0x01
    CREATE = 0x02
    UPDATE = 0x04
    DELETE = 0x08
    DEFAULT = READ


class Role(db.Document):
    name = db.StringField()
    permission = db.IntField()

    def __repr__(self):
        return "{}-{}".format(self.name, self.permission)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()


class User(db.Document):
    name = db.StringField()
    password = db.StringField()
    email = db.StringField()
    role = db.ReferenceField('Role')

    @property
    def id(self):
        return str(self._id)

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
