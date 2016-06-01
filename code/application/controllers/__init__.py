#!/usr/bin/env python
# encoding: utf-8
import auth
import user
import todo

all_bp = [
    auth.auth_bp,
    user.user_bp,
    todo.todo_bp
]
