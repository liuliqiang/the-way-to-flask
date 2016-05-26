#!/usr/bin/env python
# encoding: utf-8
from functools import wraps

from flask.ext.login import current_user, abort


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
