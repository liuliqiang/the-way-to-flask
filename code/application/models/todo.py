#!/usr/bin/env python
# encoding: utf-8
from application.extensions import db

__all__ = ['Item']


class Item(db.Document):
    content = db.StringField(required=True)
    created_date = db.DateTimeField()
    completed = db.BooleanField(default=False)
    completed_date = db.DateTimeField()
    created_by = db.ReferenceField('User', required=True)
    notes = db.ListField(db.StringField())
    priority = db.IntField()

    def __repr__(self):
        return "<Item: {} Content: {}>".format(str(self.id),
                                               self.content)

    def to_json(self):
        return {
            'id': str(self.id),
            'content': self.content,
            'completed': self.completed,
            'completed_at': self.completed_date.strftime("%Y-%m-%d %H:%M:%S") if self.completed else "",
            'created_by': self.created_by.name,
            'notes': self.notes,
            'priority': self.priority
        }
